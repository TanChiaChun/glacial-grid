from django.test import RequestFactory, SimpleTestCase

from authentication.views import acquire_csrf_token


class ViewsTests(SimpleTestCase):
    def test_acquire_csrf_token(self) -> None:
        request = RequestFactory().get("/authentication/csrftoken/")
        response = acquire_csrf_token(request)
        self.assertIn("csrftoken", response.cookies)
