from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse

from beerfest import views
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
        beer1 = factories.create_beer(bar=bar, brewery=brewery, name="Star IPA")
        beer2 = factories.create_beer(bar=bar, brewery=brewery, name="Try PA")
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
        expected_beers = self.create_user_beers()
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
