from functools import wraps

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def with_sample_user(func):
    """Create and return a sample user"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        sample_user = get_user_model().objects.create_user(
            email=kwargs.pop('email', 'example@rayhank.com'),
            password=kwargs.pop('password', 'changeme')
        )
        return func(sample_user, *args, **kwargs)

    return wrapper


@with_sample_user
def create_device(user, device_name='ESP32', device_purpose='Monitor Temperature'):
    """Create and return a sample device"""
    return models.IoTDevice.objects.create(
        user=user,
        device_name=device_name,
        device_purpose=device_purpose,
    )


@with_sample_user
def create_user(user):
    return user


class ModelTests(TestCase):
    """Test the models module"""

    def test_create_user_with_email_successful(self):
        """Test creating user with email """
        email = 'example@rayhank.com'
        password = 'changeme123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user_with_invalid_email(self):
        """Test creating user with invalid email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='changeme123'
            )

    def test_create_iotdevices(self):
        """"Test creating a new device"""
        user = get_user_model().objects.create_user(
            'example@rayhank.com',
            'changeme123',
        )
        iotdevice = models.IoTDevice.objects.create(
            user=user,
            device_name='ESP32',
            device_purpose='Monitor humidity and temperature',
        )
        self.assertEqual(str(iotdevice), f"{iotdevice.device_name} - {iotdevice.device_purpose}")

    def test_create_value(self):
        """Test creating a new value for IoT device"""
        device = create_device()
        value1 = models.DeviceValue.objects.create(
            user=device.user,
            device=device,
            value=9,
            description={
                'Car': 9,
                'Motorcycle': 10,
                'Small_Truck': 1,
                'Large_Truck': 2
            }
        )
        self.assertEqual(
            str(value1),
            f"Device : {value1.device} - Value: {value1.value} at {value1.taken_at}")
