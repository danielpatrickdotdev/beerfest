from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve, reverse

from beerfest import models, views


class URLTestBase(TestCase):
    def setUp(self):
        bar = models.Bar.objects.create(name="Test Bar")
        brewery = models.Brewery.objects.create(
            name="Test Brew Co", location="London")
        beer = models.Beer.objects.create(
            bar=bar, brewery=brewery, name="Test Pale Ale")
        user = User.objects.create(username="Mx Test")
        models.UserBeer.objects.create(user=user, beer=beer)


class TestIndexURL(URLTestBase):
    def test_index_route_uses_index_view(self):
        self.assertEqual(resolve("/").func, views.index)

    def test_index_route_reverse(self):
        self.assertEqual(reverse("index"), "/")


class TestBeerListURL(URLTestBase):
    def test_beer_list_route_uses_beer_list_view(self):
        self.assertEqual(resolve("/beers/").func, views.beer_list)

    def test_beer_list_route_reverse(self):
        self.assertEqual(reverse("beer-list"), "/beers/")


class TestBeerDetailURL(URLTestBase):
    def test_beer_detail_route_uses_beer_detail_view(self):
        match = resolve("/beers/1/")
        self.assertEqual(match.func, views.beer_detail)
        self.assertEqual(match.kwargs, {"id": 1})

    def test_beer_detail_route_reverse(self):
        self.assertEqual(reverse("beer-detail", args=(1,)), "/beers/1/")


class TestStarBeerURL(URLTestBase):
    def test_star_beer_route_uses_star_beer_view(self):
        match = resolve("/beers/1/star/")
        self.assertEqual(match.func, views.star_beer)
        self.assertEqual(match.kwargs, {"id": 1})

    def test_star_beer_route_reverse(self):
        self.assertEqual(reverse("beer-star", args=(1,)), "/beers/1/star/")


class TestUnstarBeerURL(URLTestBase):
    def test_unstar_beer_route_uses_unstar_beer_view(self):
        match = resolve("/beers/1/unstar/")
        self.assertEqual(match.func, views.unstar_beer)
        self.assertEqual(match.kwargs, {"id": 1})

    def test_unstar_beer_route_reverse(self):
        self.assertEqual(reverse("beer-unstar", args=(1,)), "/beers/1/unstar/")
