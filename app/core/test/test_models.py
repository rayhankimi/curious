from functools import wraps

from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

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
def create_device(user,
                  device_name='ESP32',
                  device_purpose='Monitor Temperature'):
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
        self.assertEqual(
            str(iotdevice),
            f"{iotdevice.device_name} - {iotdevice.device_purpose}"
        )

    def test_create_value(self):
        """Test creating a new value for IoT device"""
        device = create_device()
        value1 = models.DeviceValue.objects.create(
            user=device.user,
            device=device,
            value=9,
            motorcycle_count=2,
            car_count=3,
            smalltruck_count=4,
            bigvehicle_count=5,
        )
        self.assertEqual(
            str(value1),
            f"Device : {value1.device} at {value1.taken_at} . Value = {value1.value} "  # NOQA
            f"[{value1.motorcycle_count, value1.car_count, value1.smalltruck_count, value1.bigvehicle_count}]"  # NOQA
        )

    @patch('uuid.uuid4')
    def test_image_name_path(self, mock_uuid):
        """Test generating image path"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.image_file_path(None, 'example.png')

        self.assertEqual(file_path, f'uploads/images/{uuid}.png')

    def test_create_todo_list(self):
        """Test creating a new todo list"""
        user = create_user()
        todo_list = models.ToDoList.objects.create(
            user=user,
            title='Test Todo List',
            description='This is a test todo list',
        )

        self.assertEqual(
            str(todo_list),
            f"{todo_list.title} - {todo_list.description}"
        )
