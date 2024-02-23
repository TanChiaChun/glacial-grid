import logging

from django.test import SimpleTestCase

from productivity.models import Productivity, logger


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
