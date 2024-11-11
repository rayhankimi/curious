"""
Views for IoT Device app
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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


class DeviceValueViewSet(viewsets.ModelViewSet):
    """View for manage Device Values"""
    queryset = DeviceValue.objects.all().order_by('-id')
    serializer_class = serializers.DeviceValueSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve value for specific devices"""
        device_id = self.kwargs.get('device_pk')
        return DeviceValue.objects.filter(device__id=device_id,
                                          user=self.request.user).order_by('-taken_at')

    def perform_create(self, serializer):
        """Create a new device value with the associated devices"""
        device_id = self.kwargs.get('device_pk')
        device = IoTDevice.objects.get(id=device_id)
        serializer.save(user=self.request.user, device=device)
