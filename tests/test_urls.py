from django.test import TestCase
from django.urls import resolve, reverse

from beerfest import views
from tests import factories


class URLTestBase(TestCase):
    def setUp(self):
        factories.create_user_beer()


class TestIndexURL(URLTestBase):
    def test_index_route_uses_index_view(self):
        self.assertEqual(resolve("/").func.__name__, "IndexView")

    def test_index_route_reverse(self):
        self.assertEqual(reverse("index"), "/")


class TestBeerListURL(URLTestBase):
    def test_beer_list_route_uses_beer_list_view(self):
        self.assertEqual(resolve("/beers/").func.__name__, "BeerListView")

    def test_beer_list_route_reverse(self):
        self.assertEqual(reverse("beer-list"), "/beers/")


class TestBeerDetailURL(URLTestBase):
    def test_beer_detail_route_uses_beer_detail_view(self):
        match = resolve("/beers/1/")
        self.assertEqual(match.func.__name__, "BeerDetailView")
        self.assertEqual(match.kwargs, {"pk": 1})

    def test_beer_detail_route_reverse(self):
        self.assertEqual(reverse("beer-detail", args=(1,)), "/beers/1/")


class TestStarBeerURL(URLTestBase):
    def test_star_beer_route_uses_star_beer_view(self):
        match = resolve("/beers/1/star/")
        self.assertEqual(match.func.__name__, "StarBeerView")
        self.assertEqual(match.kwargs, {"pk": 1})

    def test_star_beer_route_reverse(self):
        self.assertEqual(reverse("beer-star", args=(1,)), "/beers/1/star/")


class TestUnstarBeerURL(URLTestBase):
    def test_unstar_beer_route_uses_unstar_beer_view(self):
        match = resolve("/beers/1/unstar/")
        self.assertEqual(match.func, views.unstar_beer)
        self.assertEqual(match.kwargs, {"id": 1})

    def test_unstar_beer_route_reverse(self):
        self.assertEqual(reverse("beer-unstar", args=(1,)), "/beers/1/unstar/")
