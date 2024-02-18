import io
from unittest.mock import patch

from django.test import SimpleTestCase

from productivity.models import Productivity


class ProductivityModelTests(SimpleTestCase):
    def test_get_frequency(self) -> None:
        productivity = Productivity(item="Calendar", frequency=0, group="Next")
        self.assertEqual(productivity.get_frequency(), "Key")

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_get_frequency_invalid_enum_value(
        self, mock_stdout: io.StringIO
    ) -> None:
        productivity = Productivity(item="Calendar", frequency=10, group="Next")
        self.assertEqual(productivity.get_frequency(), "")
        self.assertEqual(
            mock_stdout.getvalue(), "Invalid enum value for Frequency\n"
        )
