import logging
from datetime import datetime
from pathlib import Path

from django.test import SimpleTestCase

# pylint: disable=wrong-import-order
from mysite.settings import LOGGING
from productivity.models import Productivity, logger

# pylint: enable=wrong-import-order


class ProductivityModelTests(SimpleTestCase):
    def setUp(self) -> None:
        self.productivity = Productivity(
            item="Calendar",
            frequency=0,
            group="Next",
            last_check=datetime(2024, 1, 1),
        )

    def test_str(self) -> None:
        self.assertEqual(
            str(self.productivity), "[Key-Next] Calendar (01 Jan 12:00 AM)"
        )

    def test_get_frequency(self) -> None:
        self.assertEqual(self.productivity.get_frequency(), "Key")

    def test_get_frequency_invalid_enum_value(self) -> None:
        self.productivity.frequency = 10
        with self.assertLogs(logger, logging.ERROR) as logger_obj:
            self.assertEqual(self.productivity.get_frequency(), "")
            self.assertEqual(
                logger_obj.records[0].getMessage(),
                "Invalid enum value for Frequency",
            )

    def test_get_last_check(self) -> None:
        self.assertEqual(self.productivity.get_last_check(), "01 Jan 12:00 AM")


# pylint: disable-next=invalid-name
def tearDownModule() -> None:
    log_filename = LOGGING["handlers"]["file"]["filename"]
    Path(log_filename).unlink()
    print(f"Removed {log_filename}")
