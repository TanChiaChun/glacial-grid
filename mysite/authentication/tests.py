import json
import string
from random import choice

from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase

from authentication.views import authentication_login, csrftoken


def generate_random_str(length: int = 8) -> str:
    """Generate a random string.

    - Consist of ASCII lowercase & uppercase and digits.

    Args:
        length:
            Length of string to be generated.

    Returns:
        Random string.
    """
    str_seq = string.ascii_letters + string.digits

    return "".join([choice(str_seq) for i in range(length)])


class ViewsTests(TestCase):
    def setUp(self) -> None:
        self.username = generate_random_str()
        self.password = generate_random_str()

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

    def test_login_user(self) -> None:
        get_user_model().objects.create_user(
            self.username, password=self.password
        )

        response = Client().post(
            "/authentication/login/",
            data={"username": self.username, "password": self.password},
        )

        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            json.loads(response.content), {"info": "Login success"}
        )
        self.assertIn("sessionid", response.cookies)

    def test_login_user_fail_missing_data(self) -> None:
        response = Client().post("/authentication/login/")

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Missing data"}
        )

    def test_test_login_user_fail_invalid_login(self) -> None:
        response = Client().post(
            "/authentication/login/",
            data={"username": self.username, "password": self.password},
        )

        self.assertEqual(response.status_code, 401)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Invalid login"}
        )
