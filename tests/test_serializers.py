from django.test import TestCase

from beerfest.serializers import BarSerializer, BrewerySerializer

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
