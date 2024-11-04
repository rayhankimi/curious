"""
Views for IoT Device app
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from core.models import IoTDevice
from iotdevice import serializers


class DeviceViewSet(viewsets.ModelViewSet):
    """View for manage IoT Device API"""
    queryset = IoTDevice.objects.all().order_by('-id')
    serializer_class = serializers.DeviceSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve devices for authenticated user"""
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return serializer class for requests"""
        if self.action == 'list':
            return serializers.DeviceSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new device"""
        serializer.save(user=self.request.user)
