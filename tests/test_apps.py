from django.apps import apps
from django.test import TestCase

from beerfest.apps import BeerfestConfig


class TestAppConfig(TestCase):
    def test_app_name(self):
        self.assertEqual(BeerfestConfig.name, "beerfest")
        self.assertEqual(apps.get_app_config("beerfest").name, "beerfest")
