"""
Test for user API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model

from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import ToDoList
from user.serializers import TodoSerializer

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")
PERSON_URL = reverse("user:person")
TODO_LIST_URL = reverse("user:todo-list")


def todo_detail_url(todo_id):
    """Return todo detail URL"""
    return reverse('user:todo-detail', args=[todo_id])


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

        user_exist = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
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

    def test_access_other_profile(self):
        """Test that no user can access other profile"""
        res = self.client.get(PERSON_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_todo_unauthorized(self):
        """Test that no other user can access the todo list"""
        res = self.client.get(TODO_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserTests(TestCase):
    """Test API functionality for registered users"""

    def setUp(self):
        self.user = create_user(
            email='example@rayhank.com',
            password='changeme',
            name='test user',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        res = self.client.get(PERSON_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_not_allowed(self):
        """Test that post is not allowed for the user endpoint"""
        res = self.client.post(PERSON_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test changing the user profile for authenticated user"""
        payload = {
            'name': 'new name',
            'password': 'changedpw',
        }

        res = self.client.patch(PERSON_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_todo_list(self):
        """Test retrieving the todo list for the user"""
        ToDoList.objects.create(
            user=self.user,
            title='Test title',
            description='description'
        )
        ToDoList.objects.create(
            user=self.user,
            title='Test title 2',
            description='description 2'
        )

        res = self.client.get(TODO_LIST_URL)

        todos = ToDoList.objects.filter(user=self.user).order_by('-created_at')
        serializer = TodoSerializer(todos, many=True)

        results_data = res.data['results']

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(results_data), len(serializer.data))  # pastikan jumlahnya sama
        self.assertEqual(results_data, serializer.data)

    def test_create_todo(self):
        """Test creating todo"""
        payload = {
            'title': 'Test title',
            'description': 'description'
        }
        res = self.client.post(TODO_LIST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(res.data['title'], payload['title'])
        self.assertEqual(res.data['description'], payload['description'])
        self.assertIn('id', res.data)

        todo = ToDoList.objects.get(id=res.data['id'])
        self.assertEqual(todo.user, self.user)
        self.assertFalse(todo.is_completed)

    def test_update_todo(self):
        """Test updating todo (patch)"""
        todo = ToDoList.objects.create(
            user=self.user,
            title='Initial title',
            description='Initial description',
        )
        payload = {
            'title': 'Updated todo',
            'description': 'Updated description',
        }
        url = todo_detail_url(todo.id)
        res = self.client.patch(url, payload)

        todo.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(todo.title, payload['title'])
        self.assertEqual(todo.description, payload['description'])

    def test_retrieve_single_todo(self):
        """Test retrieve a single todo """
        todo = ToDoList.objects.create(
            user=self.user,
            title='Single todo',
            description='Single desc',
        )
        url = todo_detail_url(todo.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['title'], todo.title)
        self.assertEqual(res.data['description'], todo.description)

    def test_delete_todo(self):
        """Test deleting todo"""
        todo = ToDoList.objects.create(
            user=self.user,
            title='Delete me',
            description='To be removed',
        )
        url = todo_detail_url(todo.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        exists = ToDoList.objects.filter(id=todo.id).exists()
        self.assertFalse(exists)

    def test_todo_limited_to_user(self):
        """Test only getting todo for the authenticated user"""
        other_user = get_user_model().objects.create_user(
            email='other@example.com',
            password='password123'
        )
        ToDoList.objects.create(
            user=other_user,
            title='Other user todo',
            description='Should not appear'
        )

        todo = ToDoList.objects.create(
            user=self.user,
            title='My todo',
            description='Should appear'
        )

        res = self.client.get(TODO_LIST_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        results_data = res.data['results']

        self.assertEqual(len(results_data), 1)
        self.assertEqual(results_data[0]['title'], todo.title)
