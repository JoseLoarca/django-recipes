from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class TagsApiTests(TestCase):
    """ Test tags API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='myinsecurepassword!'
        )
        self.client.force_authenticate(self.user)

    def test_get_tags(self) -> None:
        """ Test retrieving tags """
        Tag.objects.create(user=self.user, name='Mediterranean')
        Tag.objects.create(user=self.user, name='Keto')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self) -> None:
        """ Test that tags returned are for the authenticated user """
        user = get_user_model().objects.create_user(
            email='dev@gmail.com',
            password='myinsecuredevpassword!'
        )

        Tag.objects.create(user=user, name='Dessert')
        tag = Tag.objects.create(user=self.user, name='Fast Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self) -> None:
        """ Test creating a new tag """
        payload = {'name': 'Asian'}
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_tag_invalid(self) -> None:
        """ Test creating a new tag with invalid payload """
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipes(self) -> None:
        """ Test filtering tags by those assigned to recipes """
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Lunch')

        recipe = Recipe.objects.create(
            title='Desayuno Chapín',
            time_minutes=15,
            price=50.00,
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_unique_tags_response(self) -> None:
        """ Test data in response is unique for filtered tags """
        tag = Tag.objects.create(user=self.user, name='Cheap')
        Tag.objects.create(user=self.user, name='Gourmet')

        recipe1 = Recipe.objects.create(
            title='Tacos',
            time_minutes=20,
            price=20.00,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Blistered Peppers',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2.tags.add(tag)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
