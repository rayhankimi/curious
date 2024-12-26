"""
Test for IoT device API
"""
import tempfile
import os

from PIL import Image

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
        return reverse(
            'user:device-value-list',
            args=[device_id]
        )
    return reverse(
        'user:device-value-detail',
        args=[device_id, value_id]
    )


def reverse_device_detail(device_id):
    return reverse(
        'user:iotdevice-detail',
        args=[device_id]
    )


def reverse_image(device_id, value_id):
    return reverse(
        'user:device-value-upload-image',
        args=[device_id, value_id]
    )


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

        response_ids = [device['id'] for device in res.data['results']]
        expected_ids = [device['id'] for device in serializer.data]

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(response_ids, expected_ids)

    def test_devices_limited_to_user(self):
        """Test that retrieving devices for authenticated user is limited"""
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
        self.assertEqual(res.data['results'], serializer.data)



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

        url = reverse_value(device_id=device.id, action='list')
        res = self.client.post(url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        device_value = DeviceValue.objects.get(id=res.data['id'])

        for key, value in payload.items():
            if key == 'user' or key == 'device':
                continue
            self.assertEqual(getattr(device_value, key), value)

        self.assertEqual(self.user, device_value.user)
        self.assertEqual(device, device_value.device)

    def test_change_value(self):
        """Test changing a device value is allowed"""
        device = create_device(user=self.user)
        value_data = {
            'user': self.user.id,
            'device': device.id,
            'value': 1,
            'motorcycle_count': 2,
            'car_count': 4,
            'smalltruck_count': 2,
            'bigvehicle_count': 1,
        }
        create_url = reverse_value(device_id=device.id, action='list')
        res = self.client.post(create_url, value_data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        value_id = res.data['id']

        detail_url = reverse_value(
            device_id=device.id,
            value_id=value_id,
            action='detail'
        )

        payload = {
            'value': 2,
            'car_count': 1,
        }
        res = self.client.patch(detail_url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_get_value_with_pagination(self):
        """Test retrieving device values with pagination and order direction"""
        device = create_device(user=self.user)

        # Buat data
        values = [
            DeviceValue.objects.create(
                user=self.user,
                device=device,
                value=i,
                motorcycle_count=i,
                car_count=i,
                smalltruck_count=i,
                bigvehicle_count=i,
            )
            for i in range(1, 21)
        ]

        url = reverse_value(device_id=device.id, action='list')

        # Pagination (page=1)
        res = self.client.get(f'{url}?page=1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        data = res.data
        self.assertIn('count', data)
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('results', data)

        self.assertEqual(data['count'], 20)
        self.assertEqual(len(data['results']), 20)  # Default page size

        # Test order_direction=first
        res = self.client.get(f'{url}?order_direction=first&page=1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.data['results']
        sorted_values = sorted(values, key=lambda x: x.taken_at)  # Urutkan manual
        self.assertEqual(results[0]['id'], sorted_values[0].id)
        self.assertEqual(results[-1]['id'], sorted_values[-1].id)

        # Test order_direction=last
        res = self.client.get(f'{url}?order_direction=last&page=1')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results = res.data['results']
        sorted_values = sorted(values, key=lambda x: x.taken_at, reverse=True)
        self.assertEqual(results[0]['id'], sorted_values[0].id)
        self.assertEqual(results[-1]['id'], sorted_values[-1].id)

    def test_device_serializer_latest_value(self):
        """Test that the device serializer includes the latest value"""
        device = create_device(user=self.user)
        DeviceValue.objects.create(
            user=self.user,
            device=device,
            value=1,
        )
        DeviceValue.objects.create(
            user=self.user,
            device=device,
            value=2
        )
        url = reverse_device_detail(device.id)
        res = self.client.get(url)
        self.assertIn('latest_value', res.data)

    def test_get_latest_value_when_no_value(self):
        """Test that latest_value is None when device has no value"""
        device = create_device(user=self.user)

        url = reverse_device_detail(device.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('latest_value', res.data)
        self.assertIsNone(res.data['latest_value'])

    def test_device_list_includes_latest_value(self):
        """Test that the device list includes the latest value"""
        device1 = create_device(user=self.user)
        device2 = create_device(user=self.user)
        DeviceValue.objects.create(
            user=self.user,
            device=device1,
            value=1,
        )
        value2 = DeviceValue.objects.create(
            user=self.user,
            device=device2,
            value=2,
        )

        res = self.client.get(DEVICE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

        for device_data in res.data['results']:
            self.assertIn('latest_value', device_data)
            if device_data['id'] == device1.id:
                self.assertIsNotNone(device_data['latest_value'])
                self.assertEqual(device_data['latest_value']['value'], 1)
            elif device_data['id'] == device2.id:
                self.assertIsNotNone(device_data['latest_value'])
                self.assertEqual(device_data['latest_value']['id'], value2.id)
                self.assertEqual(device_data['latest_value']['value'], 2)


class ImageUploadTests(TestCase):
    """Test image upload"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='example@rayhank.com',
            password='changeme'
        )
        self.client.force_authenticate(self.user)
        self.device = create_device(
            user=self.user,
        )
        self.device_value = DeviceValue.objects.create(
            user=self.user,
            device=self.device,
            value=1,
        )

    def tearDown(self):
        if self.device_value.image:
            self.device_value.image.delete()

    def test_upload_image(self):
        """Test uploading an image"""
        url = reverse_image(self.device.id, self.device_value.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'image': image_file
            }
            res = self.client.post(url, payload, format='multipart')

        self.device_value.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.device_value.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading not an image"""
        url = reverse_image(self.device.id, self.device_value.id)
        payload = {
            'image': 'notanimage'
        }
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_latest_value_include_image(self):
        """Test that hitting latest value include image"""
        device = create_device(user=self.user)
        device_value = DeviceValue.objects.create(
            user=self.user,
            device=device,
            value=1,
        )

        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            device_value.image.save('test.jpg', image_file, save=True)

        url = reverse_device_detail(device.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('latest_value', res.data)

        latest_value = res.data['latest_value']
        self.assertIsNotNone(latest_value)
        self.assertIn('image', latest_value)
        self.assertIsNotNone(latest_value['image'])

        self.assertIn('/static/media/uploads/images', latest_value['image'])

        device_value.image.delete()
