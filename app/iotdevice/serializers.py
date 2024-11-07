from rest_framework import serializers

from core.models import IoTDevice


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Device model"""

    class Meta:
        model = IoTDevice
        fields = ['id', 'device_name', 'device_purpose', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'id']


class DeviceDetailSerializer(serializers.ModelSerializer):
    """Serializer for the Device detail. Allowing put & patch methods"""

    class Meta(DeviceSerializer.Meta):
        pass
