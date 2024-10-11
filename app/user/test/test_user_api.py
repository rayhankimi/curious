"""
Test for user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")


def create_user(**params):
    """Create a user with the given parameters."""
    return get_user_model().objects.create_user(**params)


class PublicUserTests(TestCase):
    """Test avaliability of API for public user"""

    def setUp(self):
        self.client = APIClient()

    def test_create_user(self):
        """Create new user without returning a password"""
        payload = {
            'email': 'example@rayhank.com',
            'password': 'changeme',
            'name': 'test name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_already_exists(self):
        """Create a new user with that email already exists"""
        payload = {
            'email': 'example@rayhank.com',
            'password': 'changeme',
            'name': 'test name',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_same_password(self):
        """Test for creating two users with the same password is allowed"""
        user1 = {
            'email': 'example@rayhank.com',
            'password': 'changeme',
            'name': 'test name',
        }
        user2 = {
            'email': 'example2@rayhank.com',
            'password': 'changeme',
            'name': 'test name 2',
        }
        create_user(**user1)

        res = self.client.post(CREATE_USER_URL, user2)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_short_password(self):
        """Test for creating user with weak password"""
        payload = {
            'email': 'example@rayhank.com',
            'password': 'pw',
            'name': 'test name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exist = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exist)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        payload = {
            'email': 'example@rayhank.com',
            'password': 'changeme',
            'name': 'test name',
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        create_user(email='example@rayhank.com', password='correctPassword')

        payload = {
            'email': 'example@rayhank.com',
            'password': 'invalidPassword',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_password(self):
        """Test that token is not created if no password is given"""
        payload = {
            'email': 'example@rayhank.com',
            'password': '',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
