import logging
from pathlib import Path

from django.test import SimpleTestCase

# pylint: disable=wrong-import-order
from mysite.settings import LOGGING
from productivity.models import Productivity, logger

# pylint: enable=wrong-import-order


class ProductivityModelTests(SimpleTestCase):
    def test_get_frequency(self) -> None:
        productivity = Productivity(item="Calendar", frequency=0, group="Next")
        self.assertEqual(productivity.get_frequency(), "Key")

    def test_get_frequency_invalid_enum_value(self) -> None:
        productivity = Productivity(item="Calendar", frequency=10, group="Next")
        with self.assertLogs(logger, logging.ERROR) as logger_obj:
            self.assertEqual(productivity.get_frequency(), "")
            self.assertEqual(
                logger_obj.records[0].getMessage(),
                "Invalid enum value for Frequency",
            )


# pylint: disable-next=invalid-name
def tearDownModule() -> None:
    log_filename = LOGGING["handlers"]["file"]["filename"]
    Path(log_filename).unlink()
    print(f"Removed {log_filename}")
