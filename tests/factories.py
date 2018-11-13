from django.contrib.auth.models import User

from beerfest import models


def create_user(username="Mx Test"):
    return User.objects.create(username=username)


def create_brewery(name="Test Brew Co", location="Testville", nbeers=0):
    brewery = models.Brewery.objects.create(name=name, location=location)

    if nbeers > 0:
        bar = create_bar()

    for n in range(nbeers):
        create_beer(name=f"Test Beer {n}", brewery=brewery, bar=bar)

    return brewery


def create_bar(name="Test Bar"):
    return models.Bar.objects.create(name=name)


def create_beer(**kwargs):
    data = {
        "name": kwargs.get("name", "Test IPA"),
    }
    if "bar" in kwargs:
        data["bar"] = kwargs["bar"]
    else:
        data["bar"] = create_bar()

    if "brewery" in kwargs:
        data["brewery"] = kwargs["brewery"]
    else:
        data["brewery"] = create_brewery()

    if "number" in kwargs:
        data["number"] = kwargs["number"]
    if "reserved" in kwargs:
        data["reserved"] = kwargs["reserved"]
    if "abv" in kwargs:
        data["abv"] = kwargs["abv"]
    if "tasting_notes" in kwargs:
        data["tasting_notes"] = kwargs["tasting_notes"]
    if "notes" in kwargs:
        data["notes"] = kwargs["notes"]

    return models.Beer.objects.create(**data)


def star_beer(user=None, beer=None):
    if user is None:
        user = create_user()

    if beer is None:
        beer = create_beer()

    return models.StarBeer.objects.create(user=user, beer=beer)


def rate_beer(user=None, beer=None, rating=3):
    if user is None:
        user = create_user()

    if beer is None:
        beer = create_beer()

    return models.BeerRating.objects.create(user=user, beer=beer,
                                            rating=rating)
