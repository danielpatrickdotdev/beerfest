from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.db.models import Q
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import render, get_object_or_404
from django.views.generic import RedirectView, DetailView

from .models import Beer, UserBeer


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
            Q(userbeer__user=self.request.user, userbeer__starred=True) |
            Q(userbeer__user=self.request.user, userbeer__tried=True) |
            Q(userbeer__user=self.request.user, userbeer__rating__isnull=False)
        ).distinct().select_related("bar", "brewery")
        context_data["beer_list"] = beer_list

        return context_data


class BeerDetailView(DetailView):
    model = Beer


@login_required
def star_beer(request, id):
    beer = get_object_or_404(Beer, id=id)
    try:
        userbeer = UserBeer.objects.get(user=request.user, beer=beer)
    except UserBeer.DoesNotExist:
        userbeer = UserBeer(user=request.user, beer=beer)
    else:
        userbeer.starred = True
    userbeer.save()

    return HttpResponse(status=204)


@login_required
def unstar_beer(request, id):
    beer = get_object_or_404(Beer, id=id)
    userbeer = get_object_or_404(UserBeer, user=request.user, beer=beer)
    userbeer.starred = False
    userbeer.save()
    return HttpResponse(status=204)



def beer_list(request):
    beer_list = Beer.objects.distinct().select_related(
        "bar", "brewery"
    )
    if request.user.is_authenticated:
        starred = UserBeer.objects.filter(
            user_id=request.user.id,
            beer_id=OuterRef("id")
        )[:1].values("starred")

        beer_list = beer_list.annotate(
            starred=Coalesce(Subquery(starred), False)
        )

    context = {"beer_list": beer_list}
    return render(request, "beerfest/beer_list.html", context)
