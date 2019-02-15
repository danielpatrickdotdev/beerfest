from rest_framework import serializers

from .models import Bar, Brewery


class BarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bar
        fields = ["id", "name"]


class BrewerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Brewery
        fields = ["id", "name", "location"]
