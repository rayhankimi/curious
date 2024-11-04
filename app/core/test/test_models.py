from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


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
            owner=user,
            device_name='ESP32',
            device_purpose='Monitor humidity and temperature',
        )
        self.assertEqual(str(iotdevice), f"{iotdevice.device_name} - {iotdevice.device_purpose}")
