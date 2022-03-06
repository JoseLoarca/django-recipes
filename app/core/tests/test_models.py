from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@gmail.com', password='myinsecurepassword!'):
    """ Create a sample user """
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self) -> None:
        """ Test creating a new user with an email is successful """
        email = 'test@gmail.com'
        password = 'myinsecurepassword!'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self) -> None:
        """ Test the email for a new user is normalized """
        email = 'test@GmAiL.CoM'
        password = 'myinsecurepassword!'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self) -> None:
        """ Test creating user with no email raises error """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email=None,
                password='myinsecurepassword!'
            )

    def test_create_new_superuser(self) -> None:
        """ Test creating a new superuser """
        user = get_user_model().objects.create_superuser(
            email='admin@gmail.com',
            password='myinsecurepassword!'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """ Test the tag string representation """
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Dessert'
        )

        self.assertEqual(str(tag), tag.name)
