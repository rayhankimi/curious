from rest_framework import serializers

from core.models import (
    IoTDevice,
    DeviceValue
)


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Device model"""

    class Meta:
        model = IoTDevice
        fields = ['id',
                  'device_name',
                  'device_purpose',
                  'created_at',
                  'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'id']


class DeviceValueSerializer(serializers.ModelSerializer):
    """Serializer for the Device Value"""

    device = serializers.PrimaryKeyRelatedField(queryset=IoTDevice.objects.all())

    class Meta:
        model = DeviceValue
        fields = ['id',
                  'device',
                  'value',
                  'taken_at',
                  'motorcycle_count',
                  'car_count',
                  'smalltruck_count',
                  'bigvehicle_count']
        read_only_fields = ['id', 'taken_at']
