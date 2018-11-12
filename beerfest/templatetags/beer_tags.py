from django import template

from beerfest.models import StarBeer


register = template.Library()


@register.filter
def nullable_number(value):
    if value is None:
        return ""
    else:
        return value


@register.filter
def abv(value):
    if value is None:
        return "TBC"

    return f"{value:.1f}%"


@register.simple_tag
def user_starred_beer(user_id, beer_id):
    return StarBeer.objects.filter(
        user__id=user_id, beer__id=beer_id
    ).exists()


@register.inclusion_tag("beerfest/beer_list_table.html")
def display_beer_table(beer_list, user):
    return {"beer_list": beer_list, "user": user, "show_stars": False}


@register.inclusion_tag("beerfest/beer_list_table.html")
def display_beer_table_with_stars(beer_list, user):
    return {"beer_list": beer_list, "user": user, "show_stars": True}
