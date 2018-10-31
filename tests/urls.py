#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import include, path

from beerfest.views import user_profile


urlpatterns = [
    path("", include("beerfest.urls")),
    path("accounts/profile/", user_profile, name="user-profile"),
]
