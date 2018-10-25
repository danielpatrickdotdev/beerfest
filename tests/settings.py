#!/usr/bin/python
# -*- coding: utf-8 -*-

DEBUG = True
USE_TZ = True

SECRET_KEY = "KEY"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sites",
    "beerfest",
]

SITE_ID = 1

MIDDLEWARE = ()
