from decimal import Decimal

from django.test import TestCase
from django.db.migrations.executor import MigrationExecutor
from django.db import connection

from tests import factories


class TestMigration0005(TestCase):

    migrate_from = [("beerfest", "0004_auto_20181026_0212")]
    migrate_to = [("beerfest", "0005_alter_beer_abv")]

    def migrate(self, migration):
        # Reverse to the original migration
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()  # reload.
        executor.migrate(migration)

        return executor.loader.project_state(migration).apps

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

    def test_beer_abv_field_changed(self):
        beer = factories.create_beer(abv="5")
        beer.refresh_from_db()
        self.assertEqual(beer.abv, Decimal("5.0"))

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
