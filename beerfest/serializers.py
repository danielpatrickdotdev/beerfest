from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Bar, Brewery


User = get_user_model()


class BarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bar
        fields = ["id", "name"]


class BrewerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Brewery
        fields = ["id", "name", "location"]


class UserSerializer(serializers.ModelSerializer):
    starred_beers = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="beer-detail"
    )
    rated_beers = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name="beer-detail"
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "starred_beers", "rated_beers"
        ]
