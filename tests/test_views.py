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


class TestIndexView(BaseViewTest):
    def test_redirects_to_beer_list(self):
        request = self.factory.get("")
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("beer-list"))


class TestUserProfileView(BaseViewTest):
    def test_context_variables_and_template_used(self):
        """This test uses the test client, which isn't necessarily the best way
        to unit test - should ideally also test the view in other ways which
        test the view function/class directly.
        """
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

        self.client.force_login(self.user)
        response = self.client.get("/accounts/profile/")

        beer_list = list(response.context["beer_list"])
        self.assertCountEqual(beer_list, [beer1, beer2, beer3])
        user = response.context["user"]
        self.assertEqual(user, self.user)
        self.assertTemplateUsed(response, "beerfest/user_profile.html")

    def test_unauthenticated_user_gets_redirected_to_login(self):
        request = self.factory.get("")
        request.user = AnonymousUser()
        response = views.user_profile(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], self.login_url + "?next=/")
