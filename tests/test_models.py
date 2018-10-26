from django.db import IntegrityError
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

    def test_brewery_name_must_be_unique(self):
        models.Brewery.objects.create(**self.brewery_kwargs)
        with self.assertRaises(IntegrityError):
            models.Brewery.objects.create(
                name="Test Brew Co", location="Test City"
            )

    def test_default_ordering(self):
        for n in [3, 1, 5, 0]:
            kwargs = self.brewery_kwargs.copy()
            kwargs["name"] += f" {n}"
            models.Brewery.objects.create(**kwargs)

        brewery_names = models.Brewery.objects.values_list("name", flat=True)
        self.assertEqual(list(brewery_names), [
            "Test Brew Co 3",
            "Test Brew Co 1",
            "Test Brew Co 5",
            "Test Brew Co 0",
        ])


class TestBar(TestCase):
    def test_create_and_retrieve_bar(self):
        models.Bar.objects.create(name="Test Bar")
        bar = models.Bar.objects.get()

        self.assertEqual(bar.name, "Test Bar")

    def test_string_representation(self):
        bar = models.Bar.objects.create(name="Test Bar")
        self.assertEqual(str(bar), "Test Bar")

    def test_bar_name_must_be_unique(self):
        models.Bar.objects.create(name="Test Bar")
        with self.assertRaises(IntegrityError):
            models.Bar.objects.create(name="Test Bar")

    def test_default_ordering(self):
        for n in [3, 1, 5, 0]:
            models.Bar.objects.create(name=f"Test Bar {n}")

        bar_names = models.Bar.objects.values_list("name", flat=True)
        self.assertEqual(list(bar_names), [
            "Test Bar 3",
            "Test Bar 1",
            "Test Bar 5",
            "Test Bar 0",
        ])


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

    def test_beer_name_must_be_unique_with_brewery(self):
        models.Beer.objects.create(**self.beer_kwargs)

        kwargs = self.beer_kwargs.copy()
        kwargs["bar"] = models.Bar.objects.create(name="Test Bar 2")
        kwargs["reserved"] = False
        kwargs["abv"] = 55

        with self.assertRaises(IntegrityError):
            models.Beer.objects.create(**kwargs)

    def test_default_ordering(self):
        for n in [3, 1, 5, 0]:
            models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery, name=f"Test IPA {n}"
            )

        beer_names = models.Beer.objects.values_list("name", flat=True)
        self.assertEqual(list(beer_names), [
            "Test IPA 3",
            "Test IPA 1",
            "Test IPA 5",
            "Test IPA 0",
        ])


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

    def test_string_representation(self):
        ub = models.UserBeer.objects.create(user=self.user, beer=self.beer1)
        self.assertEqual(str(ub), "Mr Test and Test IPA")

    def test_beer_must_be_unique_with_user(self):
        models.UserBeer.objects.create(user=self.user, beer=self.beer1)

        kwargs = {
            "user": self.user,
            "beer": self.beer1,
            "starred": False,
            "tried": True,
            "rating": 4,
        }

        with self.assertRaises(IntegrityError):
            models.UserBeer.objects.create(**kwargs)

    def test_default_ordering(self):
        for n in [3, 1, 5, 0]:
            beer = models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery, name=f"Test Beer {n}"
            )
            models.UserBeer.objects.create(user=self.user, beer=beer)

        userbeer_strings = [
            str(ub) for ub in models.UserBeer.objects.all()
        ]

        self.assertEqual(userbeer_strings, [
            "Mr Test and Test Beer 3",
            "Mr Test and Test Beer 1",
            "Mr Test and Test Beer 5",
            "Mr Test and Test Beer 0",
        ])
