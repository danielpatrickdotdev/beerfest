from decimal import Decimal

from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.template import Context, Template
from django.test import TestCase, RequestFactory

from tests import factories

from beerfest.models import Beer, UserBeer
from beerfest.templatetags import beer_tags


class TemplateTagBaseTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        bar = factories.create_bar()
        brewery = factories.create_brewery()
        self.beer1 = factories.create_beer(
            bar=bar, brewery=brewery, name="Star PA")
        self.beer2 = factories.create_beer(
            bar=bar, brewery=brewery, name="Try IPA")
        self.beer3 = factories.create_beer(
            bar=bar, brewery=brewery, name="Mild")


class UserBeerTemplateTagBaseTest(TemplateTagBaseTest):

    def setUp(self):
        super().setUp()
        self.user = factories.create_user()
        factories.create_user_beer(
            user=self.user, beer=self.beer1, starred=True)
        factories.create_user_beer(
            user=self.user, beer=self.beer2, starred=False)


class NullableNumberFilterTest(TestCase):
    def test_None_renders_as_empty_string(self):
        rendered = Template(
            "{% load beer_tags %}"
            "{{ value|nullable_number }}"
        ).render(Context({"value": None}))

        self.assertEqual(rendered, "")

    def test_evaluates_as_expected_in_template(self):
        pairs = [
            (-1, "-1"),
            (0, "0"),
            (1, "1"),
            (99999, "99999"),
        ]

        for value, expected in pairs:
            rendered = Template(
                "{% load beer_tags %}"
                "{{ value|nullable_number }}"
            ).render(Context({"value": value}))

            self.assertEqual(rendered, expected)

    def test_returns_empty_string_when_passed_arg_None(self):
        self.assertEqual(beer_tags.nullable_number(None), "")

    def test_returns_unmodified_number(self):
        self.assertEqual(beer_tags.nullable_number(-1), -1)
        self.assertEqual(beer_tags.nullable_number(0), 0)
        self.assertEqual(beer_tags.nullable_number(1), 1)
        self.assertEqual(beer_tags.nullable_number(99999), 99999)


class ABVFilterTest(TestCase):
    def test_None_renders_as_TBC(self):
        rendered = Template(
            "{% load beer_tags %}"
            "{{ value|abv }}"
        ).render(Context({"value": None}))

        self.assertEqual(rendered, "TBC")

    def test_renders_abv_correctly(self):
        pairs = [
            (Decimal("0"), "0.0%"),
            (Decimal("0.1"), "0.1%"),
            (Decimal("1.0"), "1.0%"),
            (Decimal("10.0"), "10.0%"),
            (Decimal("99.9"), "99.9%"),
        ]

        for value, expected in pairs:
            rendered = Template(
                "{% load beer_tags %}"
                "{{ value|abv }}"
            ).render(Context({"value": value}))

            self.assertEqual(rendered, expected)

    def test_returns_TBC_when_passed_arg_None(self):
        self.assertEqual(beer_tags.abv(None), "TBC")

    def test_returns_formatted_ABV(self):
        self.assertEqual(beer_tags.abv(Decimal("0")), "0.0%")
        self.assertEqual(beer_tags.abv(Decimal("0.1")), "0.1%")
        self.assertEqual(beer_tags.abv(Decimal("1.0")), "1.0%")
        self.assertEqual(beer_tags.abv(Decimal("10.0")), "10.0%")
        self.assertEqual(beer_tags.abv(Decimal("99.9")), "99.9%")


class UserStarredBeerTemplateTagTest(UserBeerTemplateTagBaseTest):
    def test_assigns_False_in_template_if_user_has_not_starred_beer(self):
        rendered = Template(
            "{% load beer_tags %}"
            "{% user_starred_beer beer.id user.id as bool %}"
            "{% if not bool %}NOT {% endif %}STARRED"
        ).render(Context({"beer": self.beer3, "user": self.user}))

        self.assertEqual(rendered, "NOT STARRED")

    def test_assigns_True_in_template_if_user_has_starred_beer(self):
        rendered = Template(
            "{% load beer_tags %}"
            "{% user_starred_beer beer.id user.id as bool %}"
            "{% if not bool %}NOT {% endif %}STARRED"
        ).render(Context({"beer": self.beer1, "user": self.user}))

        self.assertEqual(rendered, "STARRED")

    def test_assigns_False_in_template_if_user_has_unstarred_beer(self):
        rendered = Template(
            "{% load beer_tags %}"
            "{% user_starred_beer beer.id user.id as bool %}"
            "{% if not bool %}NOT {% endif %}STARRED"
        ).render(Context({"beer": self.beer2, "user": self.user}))

        self.assertEqual(rendered, "NOT STARRED")

    def test_returns_False_if_user_has_not_starred_beer(self):
        starred = beer_tags.user_starred_beer(self.beer3.id, self.user.id)
        self.assertFalse(starred)

    def test_returns_True_if_user_has_starred_beer(self):
        starred = beer_tags.user_starred_beer(self.beer1.id, self.user.id)
        self.assertTrue(starred)

    def test_returns_False_if_user_has_unstarred_beer(self):
        starred = beer_tags.user_starred_beer(self.beer2.id, self.user.id)
        self.assertFalse(starred)


class DisplayBeerTableTemplateTagTest(UserBeerTemplateTagBaseTest):
    def test_renders_expected_table(self):
        beer_list = Beer.objects.all()
        starred = UserBeer.objects.filter(
            user_id=self.user.id,
            beer_id=OuterRef("id")
        )[:1].values("starred")
        beer_list = beer_list.annotate(
            starred=Coalesce(Subquery(starred), False)
        )
        expected = (
            "1 Star PA True | "
            "2 Try IPA False | "
            "3 Mild False | "
            "Mx Test | "
            "False\n"
        )

        rendered = Template(
            "{% load beer_tags %}"
            "{% display_beer_table beer_list user %}"
        ).render(Context({"beer_list": beer_list, "user": self.user}))

        self.assertEqual(rendered, expected)


class DisplayBeerTableWithStarsTemplateTagTest(UserBeerTemplateTagBaseTest):
    def test_renders_expected_table(self):
        beer_list = Beer.objects.all()
        starred = UserBeer.objects.filter(
            user_id=self.user.id,
            beer_id=OuterRef("id")
        )[:1].values("starred")
        beer_list = beer_list.annotate(
            starred=Coalesce(Subquery(starred), False)
        )
        expected = (
            "1 Star PA True | "
            "2 Try IPA False | "
            "3 Mild False | "
            "Mx Test | "
            "True\n"
        )

        rendered = Template(
            "{% load beer_tags %}"
            "{% display_beer_table_with_stars beer_list user %}"
        ).render(Context({"beer_list": beer_list, "user": self.user}))

        self.assertEqual(rendered, expected)
