from django.urls import path

import beerfest.views

urlpatterns = [
    path('', beerfest.views.IndexView.as_view(), name='index'),
    path('beers/', beerfest.views.beer_list, name='beer-list'),
    path('beers/<int:id>/', beerfest.views.beer_detail, name='beer-detail'),
    path('beers/<int:id>/star/',
         beerfest.views.star_beer, name='beer-star'),
    path('beers/<int:id>/unstar/',
         beerfest.views.unstar_beer, name='beer-unstar'),
]
