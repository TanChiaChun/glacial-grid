from django.test import RequestFactory, SimpleTestCase

from authentication.views import csrftoken


class ViewsTests(SimpleTestCase):
    def test_acquire_csrf_token(self) -> None:
        request = RequestFactory().get("/authentication/csrftoken/")
        response = csrftoken(request)
        self.assertIn("csrftoken", response.cookies)
