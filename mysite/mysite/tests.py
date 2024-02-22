from copy import deepcopy

from django.test import SimpleTestCase
from django.utils.log import DEFAULT_LOGGING


class SettingsTests(SimpleTestCase):
    def test_pop_mail_admins_handler(self) -> None:
        self.assertEqual(
            deepcopy(DEFAULT_LOGGING)["loggers"]["django"]["handlers"].pop(),
            "mail_admins",
        )
