from django.contrib import admin

from .models import Bar, Brewery, Beer, StarBeer


admin.site.register(Bar)
admin.site.register(Brewery)
admin.site.register(Beer)
admin.site.register(StarBeer)
