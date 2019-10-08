from django.db import migrations, models


def forwards_func(apps, schema_editor):
    Beer = apps.get_model("beerfest", "Beer")
    for beer in Beer.objects.all():
        old_abv = beer.abv
        if old_abv is None:
            continue  # skip null values

        new_abv = old_abv / 10
        if new_abv >= 100:
            raise ValueError(
                f"ABV {new_abv:.1f}% greater than or equal to 100%. "
                "Aborting migration"
            )
        beer.abv = new_abv
        beer.save()


def reverse_func(apps, schema_editor):
    Beer = apps.get_model("beerfest", "Beer")
    for beer in Beer.objects.all():
        old_abv = beer.abv
        if old_abv is None:
            continue  # skip null values

        beer.abv = int(old_abv * 10)
        beer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('beerfest', '0004_auto_20181026_0212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beer',
            name='abv',
            field=models.DecimalField(
                blank=True, decimal_places=1, max_digits=4, null=True
            ),
        ),
        migrations.RunPython(forwards_func, reverse_func),
        migrations.AlterField(
            model_name='beer',
            name='abv',
            field=models.DecimalField(
                blank=True, decimal_places=1, max_digits=3, null=True),
        ),
    ]
