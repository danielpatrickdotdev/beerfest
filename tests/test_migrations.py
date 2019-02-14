from decimal import Decimal

from django.test import TransactionTestCase
from django.core.exceptions import FieldDoesNotExist
from django.db.migrations.executor import MigrationExecutor
from django.db import connection


class MigrationTestCase(TransactionTestCase):
    migrate_to = None
    migrate_from = None

    def migrate(self, migration):
        # Reverse to the original migration
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(migration)

        return executor.loader.project_state(migration).apps


class TestMigration0005(MigrationTestCase):

    migrate_from = [("beerfest", "0004_auto_20181026_0212")]
    migrate_to = [("beerfest", "0005_alter_beer_abv")]

    def create_beers(self, apps, abvs):
        Brewery = apps.get_model("beerfest", "Brewery")
        brewery = Brewery.objects.create(
            name="Test Brewery", location="Testville")
        Bar = apps.get_model("beerfest", "Bar")
        bar = Bar.objects.create(name="Test Bar")
        Beer = apps.get_model("beerfest", "Beer")

        for n in range(len(abvs)):
            Beer.objects.create(
                bar=bar,
                brewery=brewery,
                name=f"Test Beer {n}",
                abv=abvs[n]
            )

    def test_beer_abv_of_100_raises_error(self):
        old_apps = self.migrate(self.migrate_from)
        self.create_beers(old_apps, ["1000"])
        expected_msg = (
            "ABV 100.0% greater than or equal to 100%. Aborting migration"
        )
        with self.assertRaisesMessage(ValueError, expected_msg):
            self.migrate(self.migrate_to)

    def test_beer_abv_values_changed(self):
        old_apps = self.migrate(self.migrate_from)
        values_to_test = (
            (None, None),
            ("0", Decimal("0.0")),
            ("1", Decimal("0.1")),
            ("10", Decimal("1.0")),
            ("11", Decimal("1.1")),
            ("999", Decimal("99.9")),
        )
        self.create_beers(old_apps, [v[0] for v in values_to_test])
        new_apps = self.migrate(self.migrate_to)

        Beer = new_apps.get_model("beerfest", "Beer")
        beer_list = Beer.objects.all().order_by("id")

        for n in range(len(values_to_test)):
            self.assertEqual(beer_list[n].abv, values_to_test[n][1])

    def test_reverse_migration(self):
        old_apps = self.migrate(self.migrate_to)
        values_to_test = (
            (None, None),
            ("0.0", 0),
            ("0.1", 1),
            ("1.0", 10),
            ("1.1", 11),
            ("99.9", 999),
        )
        self.create_beers(old_apps, [v[0] for v in values_to_test])
        new_apps = self.migrate(self.migrate_from)

        Beer = new_apps.get_model("beerfest", "Beer")
        beer_list = Beer.objects.all().order_by("id")

        for n in range(len(values_to_test)):
            self.assertEqual(beer_list[n].abv, values_to_test[n][1])


class TestMigration0008(MigrationTestCase):

    migrate_from = [("beerfest", "0007_auto_20181112_0844")]
    migrate_to = [("beerfest", "0008_remove_starbeer_starred")]

    def create_beers(self, apps, starred=1, unstarred=1):
        User = apps.get_model("auth", "User")
        user = User.objects.create(username="Test User")
        Brewery = apps.get_model("beerfest", "Brewery")
        brewery = Brewery.objects.create(
            name="Test Brewery", location="Testville")
        Bar = apps.get_model("beerfest", "Bar")
        bar = Bar.objects.create(name="Test Bar")
        Beer = apps.get_model("beerfest", "Beer")
        StarBeer = apps.get_model("beerfest", "StarBeer")

        for n in range(starred):
            beer = Beer.objects.create(
                bar=bar, brewery=brewery, name=f"Test Beer {n}")
            StarBeer.objects.create(user=user, beer=beer)

        try:
            StarBeer._meta.get_field("starred")
        except FieldDoesNotExist:
            pass
        else:
            for n in range(starred, starred + unstarred):
                beer = Beer.objects.create(
                    bar=bar, brewery=brewery, name=f"Test Beer {n}")
                StarBeer.objects.create(user=user, beer=beer, starred=False)

    def test_starbeer_with_starred_False_deleted(self):
        old_apps = self.migrate(self.migrate_from)
        self.create_beers(old_apps, starred=0)
        new_apps = self.migrate(self.migrate_to)

        StarBeer = new_apps.get_model("beerfest", "StarBeer")

        self.assertFalse(StarBeer.objects.all().exists())

    def test_starbeer_with_starred_True_not_deleted(self):
        old_apps = self.migrate(self.migrate_from)
        self.create_beers(old_apps, unstarred=0)
        new_apps = self.migrate(self.migrate_to)

        StarBeer = new_apps.get_model("beerfest", "StarBeer")
        starred = StarBeer.objects.all()
        star_beer = starred[0]

        self.assertEqual(len(starred), 1)
        self.assertEqual(star_beer.beer.name, "Test Beer 0")

    def test_reverse_migration(self):
        old_apps = self.migrate(self.migrate_to)
        self.create_beers(old_apps)
        new_apps = self.migrate(self.migrate_from)

        StarBeer = new_apps.get_model("beerfest", "StarBeer")
        starred = StarBeer.objects.all()
        star_beer = starred[0]

        self.assertEqual(len(starred), 1)
        self.assertEqual(star_beer.beer.name, "Test Beer 0")
