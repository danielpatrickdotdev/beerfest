from django.urls import path

import beerfest.views

urlpatterns = [
    path('', beerfest.views.IndexView.as_view(), name='index'),
    path('beers/', beerfest.views.BeerListView.as_view(), name='beer-list'),
    path('beers/<int:pk>/',
         beerfest.views.BeerDetailView.as_view(), name='beer-detail'),
    path('beers/<int:pk>/star/',
         beerfest.views.StarBeerView.as_view(), name='beer-star'),
    path('beers/<int:pk>/rating/',
         beerfest.views.BeerRatingView.as_view(), name='beer-rating'),
]
