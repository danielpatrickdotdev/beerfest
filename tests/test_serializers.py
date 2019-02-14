from django.test import TestCase

from beerfest.serializers import BarSerializer

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
