from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import Http404
from django.test import TestCase, RequestFactory
from django.urls import reverse

from beerfest import views
from beerfest.models import UserBeer
from tests import factories


class BaseViewTest(TestCase):
    def setUp(self):
        self.login_url = "/accounts/login/"
        self.factory = RequestFactory()
        self.user = factories.create_user()

    def setup_view(self, request, *args, **kwargs):
        view = self.view_class()
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view


class TestIndexView(BaseViewTest):
    def test_redirects_to_beer_list(self):
        request = self.factory.get("")
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("beer-list"))


class TestUserProfileView(BaseViewTest):
    view_class = views.UserProfileView

    def create_user_beers(self):
        bar = factories.create_bar()
        brewery = factories.create_brewery()
        beer1 = factories.create_beer(bar=bar, brewery=brewery, name="Star PA")
        beer2 = factories.create_beer(bar=bar, brewery=brewery, name="Try IPA")
        beer3 = factories.create_beer(bar=bar, brewery=brewery, name="Best")
        factories.create_beer(bar=bar, brewery=brewery, name="Unpopular Swill")

        factories.create_user_beer(user=self.user, beer=beer1, starred=True)
        factories.create_user_beer(user=self.user, beer=beer2, starred=False,
                                   tried=True)
        factories.create_user_beer(user=self.user, beer=beer3, starred=False,
                                   rating=5)

        return (beer1, beer2, beer3)

    def test_get_context_data_adds_expected_beer_objects(self):
        expected_beers = self.create_user_beers()
        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)
        view.object = None

        context_data = view.get_context_data()

        self.assertIn("beer_list", context_data)
        self.assertCountEqual(context_data["beer_list"], expected_beers)

    def test_beer_list_context_variable_contains_expected_beers(self):
        expected_beers = self.create_user_beers()
        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)

        response = view.get(request)

        self.assertIn("beer_list", response.context_data)
        self.assertCountEqual(
            response.context_data["beer_list"], expected_beers)

    def test_user_object_variable_is_logged_in_user(self):
        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)

        response = view.get(request)

        self.assertIn("user", response.context_data)
        self.assertEqual(response.context_data["user"], self.user)

    def test_get_object_returns_logged_in_user(self):
        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)

        context_object = view.get_object()

        self.assertEqual(context_object, self.user)

    def test_get_template_names(self):
        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)

        template_names = view.get_template_names()

        self.assertEqual(template_names[0], "beerfest/user_profile.html")

    def test_unauthenticated_user_gets_redirected_to_login(self):
        request = self.factory.get("")
        request.user = AnonymousUser()
        view = self.setup_view(request)

        # Use view.dispatch as this is where logged in status is checked
        response = view.dispatch(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.login_url + "?next=/")

    def test_renders_using_test_client(self):
        # Just a sanity check; almost an integration test
        expected_beers = self.create_user_beers()
        self.client.force_login(self.user)

        response = self.client.get("/accounts/profile/")
        user = response.context["user"]
        beer_list = response.context["beer_list"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "beerfest/user_profile.html")
        self.assertEqual(user, self.user)
        self.assertCountEqual(beer_list, expected_beers)


class TestBeerListView(BaseViewTest):
    view_class = views.BeerListView

    def create_beers(self):
        bar = factories.create_bar()
        brewery = factories.create_brewery()
        beer1 = factories.create_beer(bar=bar, brewery=brewery, name="IPA")
        beer2 = factories.create_beer(bar=bar, brewery=brewery, name="Mild")
        beer3 = factories.create_beer(bar=bar, brewery=brewery, name="Stout")

        return (beer1, beer2, beer3)

    def test_GETs_beer_list_context_variable(self):
        beers = self.create_beers()
        request = self.factory.get("")
        view = self.setup_view(request)

        response = view.get(request)

        self.assertIn("beer_list", response.context_data)
        self.assertCountEqual(response.context_data["beer_list"], beers)

    def test_get_queryset_returns_beer_list(self):
        beers = self.create_beers()
        request = self.factory.get("")

        view = self.setup_view(request)
        qs = view.get_queryset()

        self.assertCountEqual(qs, beers)

    def test_get_template_names(self):
        request = self.factory.get("")
        view = self.setup_view(request)
        # The following line is needed for get_template_names() to work as it
        # should (view.get assigns view.object_list before get_templates names
        # is called by view.render_to_response)
        view.object_list = view.get_queryset()

        template_names = view.get_template_names()

        self.assertEqual(template_names[0], "beerfest/beer_list.html")

    def test_renders_using_test_client(self):
        # Just a sanity check; almost an integration test
        beers = self.create_beers()

        response = self.client.get("/beers/")
        beer_list = response.context["beer_list"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "beerfest/beer_list.html")
        self.assertCountEqual(beer_list, beers)

    def test_get_queryset_annotates_starred_status_if_user_logged_in(self):
        beer1, beer2, beer3 = self.create_beers()
        factories.create_user_beer(user=self.user, beer=beer1, starred=True)
        factories.create_user_beer(user=self.user, beer=beer2, starred=False)

        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)
        qs = view.get_queryset()

        self.assertEqual(qs[0].starred, True)
        self.assertEqual(qs[1].starred, False)
        self.assertEqual(qs[2].starred, False)

    def test_GETs_annotated_beer_list_context_variable(self):
        beer1, beer2, beer3 = self.create_beers()
        factories.create_user_beer(user=self.user, beer=beer1, starred=True)
        factories.create_user_beer(user=self.user, beer=beer2, starred=False)
        user2 = factories.create_user("Ms Test")
        factories.create_user_beer(user=user2, beer=beer1, starred=False)

        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)
        response = view.get(request)
        beer_list = response.context_data["beer_list"]

        self.assertEqual(beer_list[0].starred, True)
        self.assertEqual(beer_list[1].starred, False)
        self.assertEqual(beer_list[2].starred, False)

    def test_beer_annotations_do_not_cause_duplicates(self):
        # Some types of DB queries result in duplicates - eg repeating a beer
        # for each value of starred. Test that we haven't formed such a query.
        beer1, beer2, beer3 = self.create_beers()
        factories.create_user_beer(user=self.user, beer=beer1, starred=True)
        factories.create_user_beer(user=self.user, beer=beer2, starred=False)

        user2 = factories.create_user("A Test")
        factories.create_user_beer(user=user2, beer=beer1, starred=False)
        factories.create_user_beer(user=user2, beer=beer3, starred=True)

        request = self.factory.get("")
        request.user = self.user
        view = self.setup_view(request)
        qs = view.get_queryset()

        self.assertEqual(len(qs), 3)

        request.user = user2
        view = self.setup_view(request)
        qs = view.get_queryset()

        self.assertEqual(len(qs), 3)


class TestBeerDetailView(BaseViewTest):
    view_class = views.BeerDetailView

    def create_beers(self):
        bar = factories.create_bar()
        brewery = factories.create_brewery()
        beer1 = factories.create_beer(bar=bar, brewery=brewery, name="IPA")
        beer2 = factories.create_beer(bar=bar, brewery=brewery, name="Mild")

        return (beer1, beer2)

    def test_GETs_correct_beer_context_variable(self):
        beer1, beer2 = self.create_beers()
        request = self.factory.get("")
        view = self.setup_view(request, pk=2)

        response = view.get(request)

        self.assertIn("beer", response.context_data)
        self.assertEqual(response.context_data["beer"], beer2)

    def test_get_object_returns_beer_for_given_pk(self):
        beer1, beer2 = self.create_beers()
        request = self.factory.get("")

        view = self.setup_view(request, pk=1)
        context_object1 = view.get_object()

        view = self.setup_view(request, pk=2)
        context_object2 = view.get_object()

        self.assertEqual(context_object1, beer1)
        self.assertEqual(context_object2, beer2)

    def test_get_object_and_get_with_invalid_id_raises_404(self):
        request = self.factory.get("")
        view = self.setup_view(request, pk=1)

        with self.assertRaises(Http404):
            view.get_object()

        with self.assertRaises(Http404):
            view.get(request)

    def test_get_template_names(self):
        request = self.factory.get("")
        view = self.setup_view(request)
        view.object = None

        template_names = view.get_template_names()

        self.assertEqual(template_names[0], "beerfest/beer_detail.html")

    def test_renders_using_test_client(self):
        # Just a sanity check; almost an integration test
        beer1, beer2 = self.create_beers()

        response = self.client.get("/beers/1/")
        context_beer1 = response.context["beer"]
        context_beer2 = self.client.get("/beers/2/").context["beer"]

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "beerfest/beer_detail.html")
        self.assertEqual(context_beer1, beer1)
        self.assertEqual(context_beer2, beer2)


class TestStarBeerView(BaseViewTest):
    view_class = views.StarBeerView

    def setUp(self):
        super().setUp()
        bar = factories.create_bar()
        brewery = factories.create_brewery()

        self.beer1 = factories.create_beer(
            bar=bar, brewery=brewery, name="IPA")
        self.beer2 = factories.create_beer(
            bar=bar, brewery=brewery, name="Mild")
        self.beer3 = factories.create_beer(
            bar=bar, brewery=brewery, name="Stout")

        factories.create_user_beer(user=self.user, beer=self.beer1,
                                   starred=True, tried=True, rating=5)
        factories.create_user_beer(user=self.user, beer=self.beer2,
                                   starred=False, tried=True, rating=2)

    def test_star_beer(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=3)

        view.post(request)
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer3)

        self.assertTrue(user_beer.starred)

    def test_star_beer_anonymous_forbidden(self):
        request = self.factory.post("")
        request.user = AnonymousUser()
        view = self.setup_view(request, pk=2)

        with self.assertRaises(PermissionDenied):
            # Use view.dispatch as this is where logged in status is checked
            view.dispatch(request)

        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer2)

        self.assertFalse(user_beer.starred)

    def test_star_beer_returns_204(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=3)

        response = view.post(request)

        self.assertEqual(response.status_code, 204)

    def test_star_beer_already_starred_has_no_effect(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=1)

        response = view.post(request)
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer1)

        self.assertTrue(user_beer.starred)
        self.assertTrue(user_beer.tried)
        self.assertEqual(user_beer.rating, 5)
        self.assertEqual(response.status_code, 204)

    def test_star_beer_using_test_client(self):
        # Just a sanity check; almost an integration test
        self.client.force_login(self.user)

        response = self.client.post("/beers/3/star/")
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer3)

        self.assertTrue(user_beer.starred)
        self.assertEqual(response.status_code, 204)


class TestUnstarBeerView(BaseViewTest):
    view_class = views.UnstarBeerView

    def setUp(self):
        super().setUp()
        bar = factories.create_bar()
        brewery = factories.create_brewery()

        self.beer1 = factories.create_beer(
            bar=bar, brewery=brewery, name="IPA")
        self.beer2 = factories.create_beer(
            bar=bar, brewery=brewery, name="Mild")
        self.beer3 = factories.create_beer(
            bar=bar, brewery=brewery, name="Stout")

        factories.create_user_beer(user=self.user, beer=self.beer1,
                                   starred=True, tried=True, rating=5)
        factories.create_user_beer(user=self.user, beer=self.beer2,
                                   starred=False, tried=True, rating=2)

    def test_unstar_beer(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=1)

        view.post(request)
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer1)

        self.assertFalse(user_beer.starred)

    def test_unstar_beer_anonymous_forbidden(self):
        request = self.factory.post("")
        request.user = AnonymousUser()
        view = self.setup_view(request, pk=1)

        with self.assertRaises(PermissionDenied):
            # Use view.dispatch as this is where logged in status is checked
            view.dispatch(request)

        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer1)

        self.assertTrue(user_beer.starred)

    def test_unstar_beer_returns_204(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=3)

        response = view.post(request)

        self.assertEqual(response.status_code, 204)

    def test_unstar_beer_already_unstarred_has_no_effect(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=2)

        response = view.post(request)
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer2)

        self.assertFalse(user_beer.starred)
        self.assertTrue(user_beer.tried)
        self.assertEqual(user_beer.rating, 2)
        self.assertEqual(response.status_code, 204)

    def test_unstar_beer_never_starred_creates_unstarred_userbeer_object(self):
        request = self.factory.post("")
        request.user = self.user
        view = self.setup_view(request, pk=3)

        response = view.post(request)
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer3)

        self.assertFalse(user_beer.starred)
        self.assertFalse(user_beer.tried)
        self.assertEqual(user_beer.rating, None)
        self.assertEqual(response.status_code, 204)

    def test_unstar_beer_using_test_client(self):
        # Just a sanity check; almost an integration test
        self.client.force_login(self.user)

        response = self.client.post("/beers/1/unstar/")
        user_beer = UserBeer.objects.get(user=self.user, beer=self.beer1)

        self.assertFalse(user_beer.starred)
        self.assertEqual(response.status_code, 204)


class TestStarBeerBaseView(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_missing_star_beer_attribute_results_in_error(self):
        class ConcreteView(views.StarBeerBaseView):
            pass

        request = self.factory.post("")
        view = ConcreteView()
        view.request = request
        expected_msg = "ConcreteView is missing a star_beer attribute"

        with self.assertRaisesMessage(ImproperlyConfigured, expected_msg):
            view.post(request)