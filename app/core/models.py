import os
import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone

from app import settings


def image_file_path(instance, filename):
    """Generate file path for new image"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'images', filename)


def todo_file_path(instance, filename):
    """Generate file path for new t0d0 list"""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'
    return os.path.join('uploads', 'files', filename)


def one_week_later():
    return timezone.now() + timezone.timedelta(days=7)


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **extra_fields):
        """Creates, saves and returns a new user."""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a new superuser"""
        user = self.create_user(email=email, password=password)
        user.is_superuser = True
        user.is_staff = True

        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email


class ToDoList(models.Model):
    """User T0D0 List"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(default=one_week_later)
    related_file = models.FileField(null=True, upload_to=todo_file_path)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.description}"


class IoTDevice(models.Model):
    """IotDevice model / Object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    device_name = models.CharField(max_length=255)
    device_purpose = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.device_name} - {self.device_purpose}"


class DeviceValue(models.Model):
    """Value for IoT Device Model / Object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    device = models.ForeignKey(
        'IoTDevice',
        on_delete=models.CASCADE,
        related_name='values',
    )
    value = models.IntegerField(default=0)  # Traffic Value ranged from 1 - 5
    # Each Vehicle Count
    car_count = models.IntegerField(default=0)
    motorcycle_count = models.IntegerField(default=0)
    smalltruck_count = models.IntegerField(default=0)
    bigvehicle_count = models.IntegerField(default=0)
    # Date posted
    taken_at = models.DateTimeField(auto_now_add=True)
    # Image File
    image = models.ImageField(null=True, upload_to=image_file_path)

    def __str__(self):
        return (f"Device : {self.device} at {self.taken_at} . Value = {self.value} "  # NOQA
                f"[{self.motorcycle_count, self.car_count, self.smalltruck_count, self.bigvehicle_count}]")  # NOQA
