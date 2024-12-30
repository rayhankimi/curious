from rest_framework import (
    generics,
    permissions,
    authentication, viewsets,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    TodoSerializer,
)

from core.models import ToDoList


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for the user"""
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class TodoViewSet(viewsets.ModelViewSet):
    """ViewSet for managing ToDo List (CRUD)"""
    serializer_class = TodoSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return ToDoList.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        """Create a new ToDoList"""
        serializer.save(user=self.request.user)
