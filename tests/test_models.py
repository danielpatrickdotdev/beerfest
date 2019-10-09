from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.forms import ModelForm
from django.test import TestCase

from beerfest import models
from tests import factories


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
            "Test Brew Co 0",
            "Test Brew Co 1",
            "Test Brew Co 3",
            "Test Brew Co 5",
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
        self.brewery = factories.create_brewery()
        self.bar = factories.create_bar()

        self.beer_kwargs = {
            "bar": self.bar,
            "brewery": self.brewery,
            "name": "Test IPA",
            "reserved": True,
            "abv": "4.1"
        }

        self.another_beer_kwargs = {
            "bar": self.bar,
            "brewery": self.brewery,
            "name": "Test Mild",
            "number": 1,
            "abv": "4.5",
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
        self.assertEqual(beer.abv, Decimal("4.1"))
        self.assertEqual(beer.tasting_notes, "")
        self.assertEqual(beer.notes, "")

        another_beer = models.Beer.objects.get(id=2)
        self.assertEqual(another_beer.bar, self.bar)
        self.assertEqual(another_beer.brewery, self.brewery)
        self.assertEqual(another_beer.name, "Test Mild")
        self.assertEqual(another_beer.number, 1)
        self.assertEqual(another_beer.abv, Decimal("4.5"))
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
        kwargs["abv"] = "5.5"

        with self.assertRaises(IntegrityError):
            models.Beer.objects.create(**kwargs)

    def test_create_with_valid_abv(self):
        valid_abvs = ["0.0", "0.1", "1.0", "99.9"]
        for n in range(len(valid_abvs)):
            beer = models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery,
                name=f"Test Brew {n}", abv=valid_abvs[n]
            )
            beer.refresh_from_db()
            self.assertEqual(beer.abv, Decimal(valid_abvs[n]))

    def test_create_with_too_large_abv(self):
        with self.assertRaises(InvalidOperation):
            models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery, abv="100")

    def test_validation_error_with_too_large_abv(self):
        beer = models.Beer(bar=self.bar, brewery=self.brewery, abv="100")
        expected_msg = (
            "Ensure that there are no more than "
            "2 digits before the decimal point."
        )

        with self.assertRaisesMessage(ValidationError, expected_msg):
            beer.full_clean()

    def test_default_ordering(self):
        factories.create_beer(
            bar=factories.create_bar(name="Test Bar 2"),
            brewery=self.brewery,
            name="Test IPA",
            number=1,
        )
        factories.create_beer(
            bar=self.bar,
            brewery=self.brewery,
            name="Test IPA 3",
        )
        factories.create_beer(
            bar=self.bar,
            brewery=self.brewery,
            name="Test IPA 2",
        )
        factories.create_beer(
            bar=self.bar,
            brewery=self.brewery,
            name="Test IPA 5",
            number=2,
        )
        factories.create_beer(
            bar=self.bar,
            brewery=factories.create_brewery(name="Test Brew"),
            name="Test IPA 4",
            number=3,
        )

        beer_names = models.Beer.objects.values_list("name", flat=True)
        self.assertEqual(list(beer_names), [
            "Test IPA 4",
            "Test IPA 5",
            "Test IPA 2",
            "Test IPA 3",
            "Test IPA",
        ])

    def test_access_m2m_fields(self):
        beer = factories.create_beer(bar=self.bar, brewery=self.brewery)
        user = factories.create_user()
        models.StarBeer.objects.create(beer=beer, user=user)
        models.BeerRating.objects.create(
            beer=beer, user=user, rating=5)

        beer.refresh_from_db()
        user.refresh_from_db()

        self.assertCountEqual(beer.starred_by.all(), [user])
        self.assertCountEqual(beer.rated_by.all(), [user])

        self.assertCountEqual(user.starred_beers.all(), [beer])
        self.assertCountEqual(user.rated_beers.all(), [beer])


class TestStarBeer(TestCase):
    def setUp(self):
        self.user = factories.create_user()
        self.brewery = factories.create_brewery()
        self.bar = factories.create_bar()
        self.beer1 = factories.create_beer(name="Test IPA",
                                           brewery=self.brewery, bar=self.bar)
        self.beer2 = factories.create_beer(name="Test Mild",
                                           brewery=self.brewery, bar=self.bar)

    def test_create_and_retrieve_starbeer(self):
        models.StarBeer.objects.create(user=self.user, beer=self.beer1)

        self.assertTrue(
            models.StarBeer.objects.filter(
                user=self.user, beer=self.beer1
            ).exists()
        )
        self.assertFalse(
            models.StarBeer.objects.filter(
                user=self.user, beer=self.beer2
            ).exists()
        )

    def test_string_representation(self):
        ub = models.StarBeer.objects.create(user=self.user, beer=self.beer1)
        self.assertEqual(str(ub), "Mx Test starred Test IPA")

    def test_beer_must_be_unique_with_user(self):
        models.StarBeer.objects.create(user=self.user, beer=self.beer1)

        kwargs = {
            "user": self.user,
            "beer": self.beer1,
        }

        with self.assertRaises(IntegrityError):
            models.StarBeer.objects.create(**kwargs)

    def test_default_ordering(self):
        for n in [3, 1, 5, 0]:
            beer = models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery, name=f"Test Beer {n}"
            )
            models.StarBeer.objects.create(user=self.user, beer=beer)

        starbeer_strings = [
            str(ub) for ub in models.StarBeer.objects.all()
        ]

        self.assertEqual(starbeer_strings, [
            "Mx Test starred Test Beer 3",
            "Mx Test starred Test Beer 1",
            "Mx Test starred Test Beer 5",
            "Mx Test starred Test Beer 0",
        ])


class TestBeerRating(TestCase):
    def setUp(self):
        self.user = factories.create_user()
        self.brewery = factories.create_brewery()
        self.bar = factories.create_bar()
        self.beer1 = factories.create_beer(name="Test IPA",
                                           brewery=self.brewery, bar=self.bar)
        self.beer2 = factories.create_beer(name="Test Mild",
                                           brewery=self.brewery, bar=self.bar)

    def test_create_and_retrieve_beerrating(self):
        models.BeerRating.objects.create(
            user=self.user, beer=self.beer1, rating=5
        )

        rating1 = models.BeerRating.objects.get(
            user=self.user, beer=self.beer1)

        self.assertEqual(rating1.rating, 5)

        self.assertFalse(
            models.BeerRating.objects.filter(
                user=self.user, beer=self.beer2
            ).exists()
        )

    def test_string_representation(self):
        rating = models.BeerRating.objects.create(
            user=self.user, beer=self.beer1, rating=5)
        self.assertEqual(str(rating), "Mx Test rated Test IPA 5")

    def test_beer_must_be_unique_with_user(self):
        models.BeerRating.objects.create(
            user=self.user, beer=self.beer1, rating=1
        )

        with self.assertRaises(IntegrityError):
            models.BeerRating.objects.create(
                user=self.user, beer=self.beer1, rating=2
            )

    def test_validation(self):
        class RatingForm(ModelForm):
            class Meta:
                model = models.BeerRating
                fields = ["user", "beer", "rating"]

        def populate_form(rating):
            form = RatingForm({"user": self.user.id, "beer": self.beer1.id,
                               "rating": rating})
            return form

        for invalid_value in [-1, 0, 0.5, 3.5, 5.6, 6]:
            form = populate_form(invalid_value)
            self.assertFalse(form.is_valid())

        for valid_value in [1, 2, 3, 4, 5]:
            form = populate_form(valid_value)
            self.assertTrue(form.is_valid())

    def test_default_ordering(self):
        for n in [3, 1, 5, 2]:
            beer = models.Beer.objects.create(
                bar=self.bar, brewery=self.brewery, name=f"Test Beer {n}"
            )
            models.BeerRating.objects.create(
                user=self.user, beer=beer, rating=n
            )

        beer_rating_strings = [
            str(br) for br in models.BeerRating.objects.all()
        ]

        self.assertEqual(beer_rating_strings, [
            "Mx Test rated Test Beer 3 3",
            "Mx Test rated Test Beer 1 1",
            "Mx Test rated Test Beer 5 5",
            "Mx Test rated Test Beer 2 2",
        ])
