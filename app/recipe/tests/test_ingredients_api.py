from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class IngredientsApiTest(TestCase):
    """ Test ingredients API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='myinsecurepassword!'
        )
        self.client.force_authenticate(self.user)

    def test_get_ingredients(self) -> None:
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(
            user=self.user,
            name='Avocado'
        )
        Ingredient.objects.create(
            user=self.user,
            name='Lemon'
        )

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self) -> None:
        """ Test only ingredients for the authenticated user are returned """
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Lime'
        )
        Ingredient.objects.create(
            user=get_user_model().objects.create_user(
                email='new@gmail.com',
                password='myotherinsecurepassword!'
            ),
            name='Blueberry'
        )

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self) -> None:
        """ Test create a new ingredient """
        payload = {
            'name': 'Potatoes'
        }
        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        )

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self) -> None:
        """ Test creating invalid ingredient fails """
        payload = {
            'name': ''
        }
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self) -> None:
        """ Test filtering ingredients by those assigned to recipes """
        tag1 = Ingredient.objects.create(user=self.user, name='Apples')
        tag2 = Ingredient.objects.create(user=self.user,
                                         name='Refried Black Beans')

        recipe = Recipe.objects.create(
            title='Apple Pie',
            time_minutes=15,
            price=50.00,
            user=self.user
        )
        recipe.ingredients.add(tag1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(tag1)
        serializer2 = IngredientSerializer(tag2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_unique_ingredients_response(self) -> None:
        """ Test data in response is unique for filtered ingredients """
        ingredient = Ingredient.objects.create(user=self.user, name='Sausages')
        Ingredient.objects.create(user=self.user, name='Eggs')

        recipe1 = Recipe.objects.create(
            title='Salchipapa',
            time_minutes=20,
            price=20.00,
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Omelette',
            time_minutes=5,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
