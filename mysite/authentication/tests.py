import json

from django.test import RequestFactory, SimpleTestCase

from authentication.views import authentication_login, csrftoken


class ViewsTests(SimpleTestCase):
    def test_authentication_login_get(self) -> None:
        request = RequestFactory().get("")
        response = authentication_login(request)

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Login required"}
        )

    def test_authentication_login_fail_put(self) -> None:
        request = RequestFactory().put("")
        response = authentication_login(request)

        self.assertEqual(response.status_code, 405)

    def test_csrftoken(self) -> None:
        request = RequestFactory().get("")
        response = csrftoken(request)

        self.assertIn("csrftoken", response.cookies)
