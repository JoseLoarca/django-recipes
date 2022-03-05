from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test public users API """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self) -> None:
        """ Test creating a user with a valid payload is successful """
        payload = {
            'email': 'test@gmail.com',
            'password': 'myinsecurepassword!',
            'name': 'User'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self) -> None:
        """ Test creating a user that already exists fails """
        payload = {
            'email': 'test@gmail.com',
            'password': 'myinsecurepassword!',
            'name': 'User'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self) -> None:
        """ Test that password must have more than 5 characters """
        payload = {
            'email': 'test@gmail.com',
            'password': 'pw!',
            'name': 'User'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self) -> None:
        """ Test that a token is created for the user """
        payload = {
            'email': 'test@gmail.com',
            'password': 'myinsecurepassword!',
            'name': 'User'
        }
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self) -> None:
        """ Test token is not created if invalid credentials are provided """
        create_user(email='test@gmail.com', password='myinsecurepassword!',
                    name='Wrong User')
        payload = {
            'email': 'test@gmail.com',
            'password': 'mywronginsecurepassword',
            'name': 'User'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self) -> None:
        """ Test that token is not created if user does not exist """
        payload = {
            'email': 'not-found@gmail.com',
            'password': 'myinsecurepassword!',
            'name': 'User'
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self) -> None:
        """ Test that email and password are required """
        res = self.client.post(TOKEN_URL, {'email': 'email!', 'password': ''})

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
