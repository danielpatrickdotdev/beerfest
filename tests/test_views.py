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
