from rest_framework import serializers

from core.models import (
    IoTDevice,
    DeviceValue
)


class SimpleDeviceSerializer(serializers.ModelSerializer):
    """Simplified serializer for Device to avoid recursion in nested serialization"""

    class Meta:
        model = IoTDevice
        fields = ['id', 'device_name']


class DeviceValueSerializer(serializers.ModelSerializer):
    """Serializer for the Device Value"""
    device = SimpleDeviceSerializer(read_only=True)

    class Meta:
        model = DeviceValue
        fields = [
            'id',
            'device',
            'value',
            'taken_at',
            'motorcycle_count',
            'car_count',
            'smalltruck_count',
            'bigvehicle_count',
            'image',
        ]
        read_only_fields = ['id', 'taken_at']


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Device model"""
    latest_value = serializers.SerializerMethodField()

    class Meta:
        model = IoTDevice
        fields = [
            'id',
            'device_name',
            'device_purpose',
            'created_at',
            'updated_at',
            'latest_value',
        ]
        read_only_fields = ['created_at', 'updated_at', 'id']

    def get_latest_value(self, obj):
        """Get the latest DeviceValue for the Device"""
        request = self.context.get('request', None)
        if request and hasattr(request, 'user'):
            latest_value = obj.values.filter(user=request.user).order_by('-taken_at').first()
        else:
            # If request is not available, do not filter by user
            latest_value = obj.values.order_by('-taken_at').first()
        if latest_value:
            return DeviceValueSerializer(latest_value, context=self.context).data
        return None


class ImageSerializer(serializers.ModelSerializer):
    """Serializer for the image"""

    class Meta:
        model = DeviceValue
        fields = [
            'id',
            'image',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'image': {'required': True}
        }

