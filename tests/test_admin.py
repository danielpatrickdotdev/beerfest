from django.contrib.admin import site as admin_site
from django.test import TestCase

from beerfest.models import Bar, Brewery, Beer, StarBeer


class TestBeerfestAdmin(TestCase):
    def setUp(self):
        self.registry = admin_site._registry

    def test_bar_registered_with_admin(self):
        self.assertIn(Bar, self.registry)

    def test_brewery_registered_with_admin(self):
        self.assertIn(Brewery, self.registry)

    def test_beer_registered_with_admin(self):
        self.assertIn(Beer, self.registry)

    def test_starbeer_registered_with_admin(self):
        self.assertIn(StarBeer, self.registry)
