from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from beerfest import models, views


class TestURLs(TestCase):
    def setUp(self):
        bar = models.Bar.objects.create(name="Test Bar")
        brewery = models.Brewery.objects.create(
            name="Test Brew Co", location="London")
        beer = models.Beer.objects.create(
            bar=bar, brewery=brewery, name="Test Pale Ale")
        user = User.objects.create(username="Mx Test")
        models.UserBeer.objects.create(user=user, beer=beer)

    def test_index_route_uses_index_view(self):
        self.assertEqual(resolve("/").func, views.index)

    def test_index_route_reverse(self):
        self.assertEqual(reverse("index"), "/")

    def test_beer_list_route_uses_beer_list_view(self):
        self.assertEqual(resolve("/beers/").func, views.beer_list)

    def test_beer_list_route_reverse(self):
        self.assertEqual(reverse("beer_list"), "/beers/")

    def test_beer_detail_route_uses_beer_detail_view(self):
        self.assertEqual(resolve("/beers/1/").func, views.beer_detail)

    def test_beer_detail_route_reverse(self):
        self.assertEqual(reverse("beer_detail", args=(1,)), "/beers/1/")

    def test_star_beer_route_uses_star_beer_view(self):
        self.assertEqual(resolve("/beers/1/star/").func, views.star_beer)

    def test_star_beer_route_reverse(self):
        self.assertEqual(reverse("star_beer", args=(1,)), "/beers/1/star/")

    def test_unstar_beer_route_uses_unstar_beer_view(self):
        self.assertEqual(resolve("/beers/1/unstar/").func, views.unstar_beer)

    def test_unstar_beer_route_reverse(self):
        self.assertEqual(reverse("unstar_beer", args=(1,)), "/beers/1/unstar/")
