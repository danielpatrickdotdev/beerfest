from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Brewery(models.Model):
    name = models.CharField(max_length=200, unique=True)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Bar(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Beer(models.Model):
    bar = models.ForeignKey(Bar, on_delete=models.CASCADE)
    brewery = models.ForeignKey(Brewery, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    number = models.PositiveSmallIntegerField(null=True, blank=True)
    reserved = models.BooleanField(default=False)
    abv = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True)
    tasting_notes = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} by {self.brewery.name}"

    class Meta:
        ordering = ["id"]
        unique_together = ["brewery", "name"]


class StarBeer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="starbeer")
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE,
                             related_name="starbeer")

    def __str__(self):
        return f"{self.user.username} starred {self.beer.name}"

    class Meta:
        ordering = ["id"]
        unique_together = ["user", "beer"]


class BeerRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name="beer_rating")
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE,
                             related_name="beer_rating")
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"{self.user.username} rated {self.beer.name} {self.rating}"

    class Meta:
        ordering = ["id"]
        unique_together = ["user", "beer"]
