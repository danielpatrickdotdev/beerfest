from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.views.generic import RedirectView, DetailView, ListView, View
from django.views.generic.detail import SingleObjectMixin

from .models import Beer, StarBeer


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

        beer_list = Beer.objects.filter(
            starbeer__user=self.request.user, starbeer__starred=True
        ).distinct().select_related("bar", "brewery")
        context_data["beer_list"] = beer_list

        return context_data


class BeerListView(ListView):
    model = Beer

    def get_queryset(self):
        user = getattr(self.request, "user", None)
        qs = super().get_queryset().select_related(
            "bar", "brewery"
        )
        if user is not None and user.is_authenticated:
            starred = StarBeer.objects.filter(
                user_id=user.id,
                beer_id=OuterRef("id")
            )[:1].values("starred")

            qs = qs.annotate(
                starred=Coalesce(Subquery(starred), False)
            )
        return qs


class BeerDetailView(DetailView):
    model = Beer


class StarBeerBaseView(LoginRequiredMixin, SingleObjectMixin, View):
    model = StarBeer
    http_method_names = ['post']
    raise_exception = True  # raise 403 for unauthenticated users
    star_beer = None

    def get_object(self):
        return super().get_object(queryset=Beer.objects.all())

    def post(self, request, *args, **kwargs):
        if self.star_beer is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a star_beer attribute"
            )
        beer = self.get_object()
        self.object = self.model.objects.update_or_create(
            user=self.request.user, beer=beer,
            defaults={"starred": self.star_beer}
        )
        return HttpResponse(status=204)


class StarBeerView(StarBeerBaseView):
    star_beer = True


class UnstarBeerView(StarBeerBaseView):
    star_beer = False
