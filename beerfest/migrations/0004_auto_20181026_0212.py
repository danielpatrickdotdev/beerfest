# Generated by Django 2.1.2 on 2018-10-26 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beerfest', '0003_auto_20181019_0438'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bar',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterField(
            model_name='brewery',
            name='name',
            field=models.CharField(max_length=200, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='beer',
            unique_together={('brewery', 'name')},
        ),
    ]