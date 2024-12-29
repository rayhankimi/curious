"""
Views for IoT Device app
"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import (
    viewsets,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from core.models import (
    IoTDevice,
    DeviceValue,
)
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
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new device"""
        serializer.save(user=self.request.user)

    @action(detail=True,
            methods=['get'],
            url_path='latest-value',
            permission_classes=[AllowAny])
    def latest_value(self, request, pk=None):
        """Retrieve the latest value for a specific device"""
        device = self.get_object()
        latest_value = device.values.order_by('-taken_at').first()

        if latest_value:
            serializer = serializers.DeviceValueSerializer(
                latest_value,
                context={'request': request}
            )
            return Response(serializer.data)

        return Response(
            {
                'detail': 'No values found for this device.'
            },
            status=404
        )


class DeviceValueViewSet(viewsets.ModelViewSet):
    """View for managing Device Values"""
    serializer_class = serializers.DeviceValueSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    # Set the lookup fields
    lookup_field = 'id'
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        """Retrieve values for specific devices"""
        device_id = self.kwargs.get('device_pk')
        order_direction = self.request.query_params.get('order_direction', 'last')  # Default to last

        queryset = DeviceValue.objects.filter(
            device__id=device_id,
            user=self.request.user
        ).order_by('-taken_at')

        if order_direction == 'first':
            queryset = queryset.reverse()

        return queryset

    def perform_create(self, serializer):
        """Create a new device value with the associated device"""
        device_id = self.kwargs.get('device_pk')
        device = IoTDevice.objects.get(id=device_id)
        serializer.save(user=self.request.user, device=device)

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'upload_image':
            return serializers.ImageSerializer
        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, device_pk=None, pk=None):
        """Upload an image to a device value"""
        # Retrieve the device value instance
        device_value = self.get_object()
        serializer = self.get_serializer(
            device_value,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="order_direction",
                description="Order direction of the results. "
                            "Use 'last' (default) for latest first or 'first' for earliest first.",
                required=False,
                type=str,
                enum=['first', 'last']
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Retrieve a list of device values"""
        return super().list(request, *args, **kwargs)
