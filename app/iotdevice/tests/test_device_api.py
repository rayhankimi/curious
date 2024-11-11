"""
Test for IoT device API
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    IoTDevice,
    DeviceValue,
)

from iotdevice.serializers import DeviceSerializer

DEVICE_URL = reverse('user:iotdevice-list')


def reverse_value(device_id, value_id=0, action='detail'):
    """Reverse from device value"""
    if action == 'list':
        return reverse('user:device-value-list', args=[device_id])
    return reverse('user:device-value-detail', args=[device_id, value_id])


def reverse_device_detail(device_id):
    return reverse('user:iotdevice-detail', args=[device_id])


def create_device(user, **params):
    """Create a new device"""
    defaults = {
        'device_name': 'ESP32',
        'device_purpose': 'Monitor Temperature',
    }
    defaults.update(params)

    device = IoTDevice.objects.create(user=user, **defaults)
    return device


def create_user(**params):
    """Create a new user"""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(
            email='example@rayhank.com',
            password='changeme'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_device_list(self):
        """Test retrieving a list of devices"""
        create_device(user=self.user)
        create_device(user=self.user)

        res = self.client.get(DEVICE_URL)

        devices = IoTDevice.objects.filter(user=self.user).order_by('-id')
        serializer = DeviceSerializer(devices, many=True)

        response_ids = [device['id'] for device in res.data]
        expected_ids = [device['id'] for device in serializer.data]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ids, expected_ids)

    def test_recipes_limited_to_user(self):
        """Test that retrieving recipes for authenticated user is limited"""
        user2 = create_user(
            email='anotheruser@rayhank.com',
            password='changeme123'
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

    def test_partial_update_device(self):
        """Test partial update of a device"""
        original_purpose = 'Monitor Temperature'
        device = create_device(
            user=self.user,
            device_name='ESP32',
            device_purpose=original_purpose,
        )
        payload = {
            'device_purpose': 'Monitor Humidity',
        }

        url = reverse_device_detail(device.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        device.refresh_from_db()
        self.assertNotEqual(res.data['device_purpose'], original_purpose)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.device_name, res.data['device_name'])

    def test_full_update_device(self):
        """Test full update of a device"""
        device = create_device(
            user=self.user,
            device_name='ESP32',
            device_purpose='Display Traffic Light',
        )

        payload = {
            'device_name': 'Raspberry Pi',
            'device_purpose': 'Get Traffic Details',
        }

        url = reverse_device_detail(device.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        device.refresh_from_db()

        for key, value in payload.items():
            self.assertEqual(getattr(device, key), value)

        self.assertEqual(device.user, self.user)

    def test_update_user_not_allowed(self):
        """Test that updating user is forbidden"""
        another_user = create_user(
            email='another@rayhank.com',
            password='changeme123',
        )
        device = create_device(user=self.user)
        payload = {
            'user': another_user.id,
        }
        self.client.patch(DEVICE_URL, payload)

        device.refresh_from_db()
        self.assertEqual(device.user, self.user)

    def test_create_device_with_values(self):
        """Test creating a new device with value"""
        device = create_device(user=self.user)

        payload = {
            'user': self.user.id,
            'device': device.id,
            'value': 3,
            'motorcycle_count': 5,
            'car_count': 2,
            'smalltruck_count': 1,
            'bigvehicle_count': 1,
        }

        # Gunakan `reverse_value` untuk mendapatkan URL yang benar
        url = reverse_value(device_id=device.id, action='list')
        res = self.client.post(url, payload)

        # Pastikan status code adalah 201 CREATED
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # Ambil objek DeviceValue yang baru dibuat dari database
        device_value = DeviceValue.objects.get(id=res.data['id'])

        # Verifikasi bahwa data tersimpan dengan benar
        for key, value in payload.items():
            if key == 'user' or key == 'device':
                continue
            self.assertEqual(getattr(device_value, key), value)

        # Verifikasi user dan device yang terkait
        self.assertEqual(self.user, device_value.user)
        self.assertEqual(device, device_value.device)
