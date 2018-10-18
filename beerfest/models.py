from django.db import models
from django.conf import settings


class Brewery(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Bar(models.Model):
    name = models.CharField(max_length=200)

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
    abv = models.PositiveSmallIntegerField(null=True, blank=True)
    tasting_notes = models.TextField()
    notes = models.TextField()


    def __str__(self):
        return f"{self.name} by {self.brewery.name}"


    class Meta:
        ordering = ["id"]


class UserBeer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    beer = models.ForeignKey(Beer, on_delete=models.CASCADE)
    starred = models.BooleanField(default=True)
    tried = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(null=True, blank=True)


    def __str__(self):
        return f"{self.user.username} and {self.beer.name}"


    class Meta:
        ordering = ["id"]
