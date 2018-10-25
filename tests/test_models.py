from django.test import TestCase
from django.contrib.auth.models import User

from beerfest import models


class TestBrewery(TestCase):
    def setUp(self):
        self.brewery_kwargs = {"name": "Test Brew Co", "location": "Testville"}

    def test_create_and_retrieve_brewery(self):
        models.Brewery.objects.create(**self.brewery_kwargs)
        brewery = models.Brewery.objects.get()

        self.assertEqual(brewery.name, "Test Brew Co")
        self.assertEqual(brewery.location, "Testville")

    def test_string_representation(self):
        brewery = models.Brewery.objects.create(**self.brewery_kwargs)
        self.assertEqual(str(brewery), "Test Brew Co")


class TestBar(TestCase):
    def test_create_and_retrieve_bar(self):
        models.Bar.objects.create(name="Test Bar")
        bar = models.Bar.objects.get()

        self.assertEqual(bar.name, "Test Bar")

    def test_string_representation(self):
        bar = models.Bar.objects.create(name="Test Bar")
        self.assertEqual(str(bar), "Test Bar")


class TestBeer(TestCase):
    def setUp(self):
        self.brewery = models.Brewery.objects.create(
            name="Test Brew Co", location="Testville")
        self.bar = models.Bar.objects.create(name="Test Bar")

        self.beer_kwargs = {
            "bar": self.bar,
            "brewery": self.brewery,
            "name": "Test IPA",
            "reserved": True,
            "abv": 41
        }

        self.another_beer_kwargs = {
            "bar": self.bar,
            "brewery": self.brewery,
            "name": "Test Mild",
            "number": 1,
            "abv": 45,
            "tasting_notes": "Dark brown with low IBU",
            "notes": "N/A"
        }

    def test_create_and_retrieve_beer(self):
        models.Beer.objects.create(**self.beer_kwargs)
        models.Beer.objects.create(**self.another_beer_kwargs)

        beer = models.Beer.objects.get(id=1)
        self.assertEqual(beer.bar, self.bar)
        self.assertEqual(beer.brewery, self.brewery)
        self.assertEqual(beer.name, "Test IPA")
        self.assertEqual(beer.reserved, True)
        self.assertEqual(beer.abv, 41)
        self.assertEqual(beer.tasting_notes, "")
        self.assertEqual(beer.notes, "")

        another_beer = models.Beer.objects.get(id=2)
        self.assertEqual(another_beer.bar, self.bar)
        self.assertEqual(another_beer.brewery, self.brewery)
        self.assertEqual(another_beer.name, "Test Mild")
        self.assertEqual(another_beer.number, 1)
        self.assertEqual(another_beer.abv, 45)
        self.assertEqual(another_beer.tasting_notes, "Dark brown with low IBU")
        self.assertEqual(another_beer.notes, "N/A")

    def test_string_representation(self):
        beer = models.Beer.objects.create(**self.beer_kwargs)
        another_beer = models.Beer.objects.create(**self.another_beer_kwargs)

        self.assertEqual(str(beer), "Test IPA by Test Brew Co")
        self.assertEqual(str(another_beer), "Test Mild by Test Brew Co")


class TestUserBeer(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="Mr Test")
        self.brewery = models.Brewery.objects.create(
            name="Test Brew Co", location="Testville")
        self.bar = models.Bar.objects.create(name="Test Bar")
        self.beer1 = models.Beer.objects.create(
            bar=self.bar, brewery=self.brewery, name="Test IPA")
        self.beer2 = models.Beer.objects.create(
            bar=self.bar, brewery=self.brewery, name="Test Mild")
        self.beer3 = models.Beer.objects.create(
            bar=self.bar, brewery=self.brewery, name="Test DIPA")

    def test_create_and_retrieve_userbeer(self):
        models.UserBeer.objects.create(user=self.user, beer=self.beer1)
        models.UserBeer.objects.create(user=self.user, beer=self.beer2,
                                       starred=False, tried=True, rating=5)
        models.UserBeer.objects.create(user=self.user, beer=self.beer3,
                                       starred=True, tried=False, rating=None)

        user_beer1 = models.UserBeer.objects.get(id=1)
        user_beer2 = models.UserBeer.objects.get(id=2)
        user_beer3 = models.UserBeer.objects.get(id=3)

        self.assertEqual(user_beer1.user, self.user)
        self.assertEqual(user_beer1.beer, self.beer1)
        self.assertEqual(user_beer1.starred, True)
        self.assertEqual(user_beer1.tried, False)
        self.assertEqual(user_beer1.rating, None)

        self.assertEqual(user_beer2.user, self.user)
        self.assertEqual(user_beer2.beer, self.beer2)
        self.assertEqual(user_beer2.starred, False)
        self.assertEqual(user_beer2.tried, True)
        self.assertEqual(user_beer2.rating, 5)

        self.assertEqual(user_beer3.user, self.user)
        self.assertEqual(user_beer3.beer, self.beer3)
        self.assertEqual(user_beer3.starred, True)
        self.assertEqual(user_beer3.tried, False)
        self.assertEqual(user_beer3.rating, None)
