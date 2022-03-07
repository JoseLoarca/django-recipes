from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """ Build URL for recipe details """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Featured'):
    """ Create and return a sample tag """
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Salmon'):
    """ Create and return a sample ingredient """
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):
    """ Create and return a sample recipe """
    defaults = {
        'title': 'My sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class RecipesApiTests(TestCase):
    """ Test recipes API """

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='myinsecurepassword!'
        )
        self.client.force_authenticate(self.user)

    def test_get_recipes(self) -> None:
        """ Test get recipes list """
        sample_recipe(user=self.user, title='Rellenitos')
        sample_recipe(user=self.user, title='Chuchitos')

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 2)

    def test_recipes_limited_to_user(self) -> None:
        """ Test retrieving recipes for a user """
        new_user = get_user_model().objects.create_user(
            email='new@gmail.com',
            password='mynewpassword!'
        )

        sample_recipe(user=self.user)
        sample_recipe(user=new_user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 1)

    def test_view_recipe_detail(self) -> None:
        """ Test getting recipe details  """
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self) -> None:
        """ Test creating recipe """
        payload = {
            'title': 'Tamales',
            'time_minutes': 120,
            'price': 100.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self) -> None:
        """ Test creating a recipe with tags """
        tag1 = sample_tag(user=self.user, name='Healthy')
        tag2 = sample_tag(user=self.user, name='Popular')

        payload = {
            'title': 'Guacamol',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 10,
            'price': 10.00
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_ingredients(self) -> None:
        """ Test creating recipe with ingredients """
        ingredient1 = sample_ingredient(user=self.user, name='Avocado')
        ingredient2 = sample_ingredient(user=self.user, name='Lemon')

        payload = {
            'title': 'Avocado Toast',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 15,
            'price': 15.00
        }

        res = self.client.post(RECIPES_URL, payload)

        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
