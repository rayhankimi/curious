"""
Test for IoT device API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import IoTDevice

from iotdevice.serializers import DeviceSerializer

DEVICE_URL = reverse('iotdevice:iotdevice-list')


def create_device(user, **params):
    """Create a new device"""
    defaults = {
        'device_name': 'ESP32',
        'device_purpose': 'Monitor Temperature',
    }
    defaults.update(params)

    device = IoTDevice.objects.create(user=user, **defaults)
    return device


class PublicDeviceApiTests(TestCase):
    """Test unauthenticated device API access"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        res = self.client.get(DEVICE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateDeviceApiTests(TestCase):
    """Test authenticated device API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'example@rayhank.com',
            'changeme'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_device_list(self):
        """Test retrieving a list of devices"""
        # Buat dua perangkat dengan user yang sama
        device1 = create_device(user=self.user)
        device2 = create_device(user=self.user)

        # Lakukan request GET pada endpoint
        res = self.client.get(DEVICE_URL)

        # Ambil perangkat dari database dengan filter dan urutan yang sesuai
        devices = IoTDevice.objects.filter(user=self.user).order_by('-id')
        serializer = DeviceSerializer(devices, many=True)

        # Cocokkan id dari respons API dan serializer data
        response_ids = [device['id'] for device in res.data]
        expected_ids = [device['id'] for device in serializer.data]

        # Assertions
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ids, expected_ids)

    def test_recipes_limited_to_user(self):
        """Test that retrieving recipes for authenticated user is limited"""
        user2 = get_user_model().objects.create_user(
            'anotheruser@rayhank.com',
            'changeme123',
        )
        create_device(user=self.user)
        create_device(user=user2)

        res = self.client.get(DEVICE_URL)

        devices = IoTDevice.objects.filter(user=self.user)
        serializer = DeviceSerializer(devices, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

        self.assertEqual(res.data, serializer.data)

    def test_create_device(self):
        """Test creating a new device"""
        payload = {
            'device_name': 'ESP32',
            'device_purpose': 'Monitor Temperature',
        }
        res = self.client.post(DEVICE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        device = IoTDevice.objects.get(id=res.data['id'])

        for key, value in payload.items():
            self.assertEqual(getattr(device, key), value)
        self.assertEqual(device.user, self.user)
