import logging
from datetime import date, datetime
from pathlib import Path

from django.test import TestCase

# pylint: disable=wrong-import-order
from mysite.settings import LOGGING
from productivity.models import Productivity, logger

# pylint: enable=wrong-import-order


class ProductivityModelTests(TestCase):
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

    def test_crud(self) -> None:
        self.productivity.save()

        productivities = Productivity.objects.all()
        self.assertEqual(len(productivities), 1)
        self.assertEqual(productivities[0].item, "Calendar")
        self.assertEqual(productivities[0].frequency, 0)
        self.assertEqual(productivities[0].group, "Next")
        self.assertEqual(productivities[0].last_check.date(), date.today())
        self.assertEqual(productivities[0].last_check_undo, datetime.min)

        self.productivity.item = "To-Do"
        self.productivity.save()
        productivities = Productivity.objects.all()
        self.assertEqual(len(productivities), 1)
        self.assertEqual(productivities[0].item, "To-Do")
        self.assertEqual(productivities[0].frequency, 0)

        self.assertEqual(
            self.productivity.delete(), (1, {"productivity.Productivity": 1})
        )
        self.assertEqual(len(Productivity.objects.all()), 0)


# pylint: disable-next=invalid-name
def tearDownModule() -> None:
    log_filename = LOGGING["handlers"]["file"]["filename"]
    try:
        Path(log_filename).unlink()
        print(f"Removed {log_filename}")
    except PermissionError:
        print(f"{log_filename} not removed")
