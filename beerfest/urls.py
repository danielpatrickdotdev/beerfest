from django.urls import path

import beerfest.views

urlpatterns = [
    path('', beerfest.views.index, name='index'),
    path('beers/', beerfest.views.beer_list, name='beer_list'),
    path('beers/<int:id>/', beerfest.views.beer_detail, name='beer_detail'),
    path('beers/<int:id>/star/',
         beerfest.views.star_beer, name='star_beer'),
    path('beers/<int:id>/unstar/',
         beerfest.views.unstar_beer, name='unstar_beer'),
]
