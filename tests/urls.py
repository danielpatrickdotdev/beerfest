#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import include, path

from beerfest.views import UserProfileView


urlpatterns = [
    path("", include("beerfest.urls")),
    path("accounts/profile/", UserProfileView.as_view(), name="user-profile"),
]
