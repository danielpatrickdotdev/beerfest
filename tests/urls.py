#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.urls import include, path


urlpatterns = [
    path("", include("beerfest.urls")),
]
