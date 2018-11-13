import json

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import ModelForm
from django.http import HttpResponse
from django.db.models.expressions import Exists, OuterRef
from django.views.generic import RedirectView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from .models import Beer, StarBeer, BeerRating


User = get_user_model()


class IndexView(RedirectView):
    pattern_name = "beer-list"


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = "user"
    template_name = "beerfest/user_profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        starred_beers = Beer.objects.filter(
            starbeer__user=self.request.user
        ).distinct().select_related("bar", "brewery")
        context_data["starred_beers"] = starred_beers

        return context_data


class BeerListView(ListView):
    model = Beer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        qs = super().get_queryset().select_related(
            "bar", "brewery"
        )
        if user is not None and user.is_authenticated:
            star_beer = StarBeer.objects.filter(
                user=user.pk,
                beer=OuterRef("pk")
            )
            qs = qs.annotate(starred=Exists(star_beer))
        return qs


class BeerDetailView(DetailView):
    model = Beer


class StarBeerView(LoginRequiredMixin, SingleObjectMixin, View):
    model = StarBeer
    http_method_names = ['delete', 'put']
    raise_exception = True  # raise 403 for unauthenticated users

    def get_object(self):
        return super().get_object(queryset=Beer.objects.all())

    def delete(self, request, *args, **kwargs):
        beer = self.get_object()
        try:
            obj = self.model.objects.get(
                user=self.request.user, beer=beer
            )
        except self.model.DoesNotExist:
            pass
        else:
            obj.delete()
        return HttpResponse(status=204)

    def put(self, request, *args, **kwargs):
        beer = self.get_object()
        self.object = self.model.objects.get_or_create(
            user=self.request.user, beer=beer
        )
        return HttpResponse(status=204)


class RatingForm(ModelForm):
    class Meta:
        model = BeerRating
        fields = ["rating"]


class BeerRatingView(LoginRequiredMixin, SingleObjectMixin, View):
    model = BeerRating
    http_method_names = ['delete', 'put']
    raise_exception = True  # raise 403 for unauthenticated users

    def get_object(self):
        return super().get_object(queryset=Beer.objects.all())

    def delete(self, request, *args, **kwargs):
        beer = self.get_object()
        try:
            obj = self.model.objects.get(
                user=self.request.user, beer=beer
            )
        except self.model.DoesNotExist:
            pass
        else:
            obj.delete()
        return HttpResponse(status=204)

    def put(self, request, *args, **kwargs):
        beer = self.get_object()
        body = json.loads(request.body)
        form = RatingForm(body)

        if form.is_valid():
            self.model.objects.update_or_create(
                user=request.user, beer=beer, defaults=form.cleaned_data)

            return HttpResponse(status=204)
        else:
            return HttpResponse(status=400)
