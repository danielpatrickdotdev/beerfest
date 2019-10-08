from django.test import TestCase
from django.urls import reverse

from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from beerfest.serializers import (
    BarSerializer, BrewerySerializer, UserSerializer
)

from tests import factories


class TestBarSerializer(TestCase):

    def setUp(self):
        self.serializer = BarSerializer(instance=factories.create_bar())

    def test_contains_expected_fields(self):
        self.assertCountEqual(self.serializer.data.keys(), ["id", "name"])

    def test_id_field_content(self):
        self.assertEqual(self.serializer.data["id"], 1)

    def test_name_field_content(self):
        self.assertEqual(self.serializer.data["name"], "Test Bar")


class TestBrewerySerializer(TestCase):

    def setUp(self):
        self.serializer = BrewerySerializer(
            instance=factories.create_brewery()
        )

    def test_contains_expected_fields(self):
        self.assertCountEqual(
            self.serializer.data.keys(), ["id", "name", "location"]
        )

    def test_id_field_content(self):
        self.assertEqual(self.serializer.data["id"], 1)

    def test_name_field_content(self):
        self.assertEqual(self.serializer.data["name"], "Test Brew Co")

    def test_location_field_content(self):
        self.assertEqual(self.serializer.data["location"], "Testville")


class TestUserSerializer(TestCase):

    def context(self, user_id=1):
        return {
            'request': Request(APIRequestFactory().get(f'/users/{user_id}/')),
        }

    def beer_detail(self, beer_id):
        request = self.context()['request']
        relative_uri = reverse('beer-detail', args=(beer_id,))
        return request.build_absolute_uri(relative_uri)

    def setUp(self):
        self.user = factories.create_user()
        self.serializer = UserSerializer(
            instance=self.user,
            context=self.context(1),
        )

        self.beer1 = factories.create_beer(name="Test1")
        self.beer2 = factories.create_beer(name="Test2")

        factories.star_beer(self.user, self.beer1)
        factories.star_beer(self.user, self.beer2)
        factories.rate_beer(self.user, self.beer1)
        factories.rate_beer(self.user, self.beer2)

        self.user2 = factories.create_user(username="T Est")
        self.serializer2 = UserSerializer(
            instance=self.user2,
            context=self.context(2),
        )

    def test_contains_expected_fields(self):
        expected_fields = [
            "id", "username", "email", "starred_beers", "rated_beers"
        ]
        self.assertCountEqual(self.serializer.data.keys(), expected_fields)

    def test_id_field_content(self):
        self.assertEqual(self.serializer.data["id"], 1)

    def test_name_field_content(self):
        self.assertEqual(self.serializer.data["username"], "Mx Test")

    def test_location_field_content(self):
        self.assertEqual(self.serializer.data["email"], "test@example.com")

    def test_starred_beers_field_content(self):
        self.assertCountEqual(
            self.serializer.data["rated_beers"],
            [self.beer_detail(1), self.beer_detail(2)],
        )

    def test_starred_beers_empty(self):
        self.assertCountEqual(
            self.serializer2.data["rated_beers"],
            []
        )

    def test_rated_beers_field_content(self):
        self.assertCountEqual(
            self.serializer.data["rated_beers"],
            [self.beer_detail(1), self.beer_detail(2)],
        )

    def test_rated_beers_empty(self):
        self.assertCountEqual(
            self.serializer2.data["rated_beers"],
            []
        )
