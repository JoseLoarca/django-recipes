from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

TAGS_URL = reverse('recipe:tag-list')
INGREDIENTS_URL = reverse('recipe:ingredient-list')
RECIPES_URL = reverse('recipe:recipe-list')


class UnauthorizedApiTests(TestCase):
    """ Test unauthorized API calls """

    def setUp(self) -> None:
        self.client = APIClient()

    def test_tags_auth_required(self) -> None:
        """ Test authentication is required for retrieving tags """
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ingredients_auth_required(self) -> None:
        """ Test authentication is required for retrieving ingredients """
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recipes_auth_required(self) -> None:
        """ Test authentication is required for retrieving recipes """
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
