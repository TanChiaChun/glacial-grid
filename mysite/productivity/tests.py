import json
import logging
from datetime import date, datetime
from pathlib import Path

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

# pylint: disable=wrong-import-order
from mysite.settings import LOGGING
from productivity.models import Productivity, logger
from productivity.views import create_productivity, index

# pylint: enable=wrong-import-order


class ProductivityModelTests(TestCase):
    def setUp(self) -> None:
        self.productivity = Productivity(
            item="Calendar",
            frequency=0,
            group="Next",
            last_check=datetime(2024, 1, 1),
        )

    def test_deserialize_json(self) -> None:
        j = {
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": "2024-01-01T00:00:00",
            "last_check_undo": "0001-01-01T00:00:00",
        }
        productivity = Productivity.deserialize_json(j)

        self.assertEqual(productivity.item, "Calendar")
        self.assertEqual(productivity.frequency, 0)
        self.assertEqual(productivity.group, "Next")
        self.assertEqual(productivity.last_check, datetime(2024, 1, 1))
        self.assertEqual(productivity.last_check_undo, datetime.min)

    def test_deserialize_json_key_error(self) -> None:
        j = {
            "ite": "Calendar",
            "frequency": "Key",
        }
        with self.assertRaises(KeyError) as cm:
            Productivity.deserialize_json(j)
        self.assertEqual(cm.exception.args[0], "item")

    def test_deserialize_json_validation_error_item(self) -> None:
        j = {
            "item": "Calendar" * 26,
            "frequency": "Key",
            "group": "Next",
            "last_check": "2024-01-01T00:00:00",
            "last_check_undo": "0001-01-01T00:00:00",
        }
        with self.assertRaises(ValidationError) as cm:
            Productivity.deserialize_json(j)
        self.assertIn("item", cm.exception.args[0])

    def test_deserialize_json_validation_error_frequency(self) -> None:
        j = {
            "item": "Calendar",
            "frequency": "Ke",
        }
        with self.assertRaises(ValidationError) as cm:
            Productivity.deserialize_json(j)
        self.assertEqual(
            cm.exception.args[0], "Invalid enum name for Frequency"
        )

    def test_deserialize_json_validation_error_datetime(self) -> None:
        j = {
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": "",
        }
        with self.assertRaises(ValidationError) as cm:
            Productivity.deserialize_json(j)
        self.assertEqual(
            cm.exception.args[0], "Invalid date_string format for last_check"
        )

    def test_parse_iso_datetime(self) -> None:
        self.assertEqual(
            Productivity.parse_iso_datetime(
                "2024-01-01T00:00:00", "last_check"
            ),
            datetime(2024, 1, 1),
        )

    def test_parse_iso_datetime_validation_error(self) -> None:
        with self.assertRaises(ValidationError) as cm:
            Productivity.parse_iso_datetime("", "last_check")
        self.assertEqual(
            cm.exception.args[0], "Invalid date_string format for last_check"
        )

    def test_str(self) -> None:
        self.assertEqual(
            str(self.productivity), "[Key-Next] Calendar (01 Jan 12:00 AM)"
        )

    def test_str_empty_instance(self) -> None:
        self.assertEqual(str(Productivity()), "[-]  ()")

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

    def test_serialize_json(self) -> None:
        self.productivity.id = 1
        expected = {
            "id": "1",
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": "2024-01-01T00:00:00",
            "last_check_undo": "0001-01-01T00:00:00",
        }
        self.assertDictEqual(self.productivity.serialize_json(), expected)

    def test_serialize_json_empty_instance(self) -> None:
        expected = {
            "id": "None",
            "item": "",
            "frequency": "",
            "group": "",
            "last_check": "",
            "last_check_undo": "0001-01-01T00:00:00",
        }
        self.assertDictEqual(Productivity().serialize_json(), expected)

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
        self.assertEqual(Productivity.objects.count(), 0)


class ViewsTest(TestCase):
    def test_create_productivity_success(self) -> None:
        self.assertEqual(Productivity.objects.count(), 0)

        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "0", "group": "Next"},
        )
        response = create_productivity(request)

        self.assertEqual(response.status_code, 201)

        j = json.loads(response.content)
        self.assertEqual(len(j), 6)
        self.assertIn("id", j)
        self.assertEqual(j["item"], "Calendar")
        self.assertEqual(j["frequency"], "Key")
        self.assertEqual(j["group"], "Next")
        self.assertIs(
            j["last_check"].startswith(date.today().isoformat()), True
        )
        self.assertEqual(j["last_check_undo"], "0001-01-01T00:00:00")

        self.assertEqual(Productivity.objects.count(), 1)

        self.assertEqual(
            Productivity.objects.all().delete(),
            (1, {"productivity.Productivity": 1}),
        )
        self.assertEqual(Productivity.objects.count(), 0)

    def test_create_productivity_fail_get(self) -> None:
        request = RequestFactory().get("productivity/")
        response = create_productivity(request)

        self.assertEqual(response.status_code, 405)

    def test_create_productivity_fail_missing_data(self) -> None:
        request = RequestFactory().post("productivity/")
        response = create_productivity(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Missing data"}
        )

    def test_create_productivity_fail_invalid_data_item(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar" * 26, "frequency": "0", "group": "Next"},
        )
        response = create_productivity(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_create_productivity_fail_invalid_data_frequency(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "10", "group": "Next"},
        )
        response = create_productivity(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_create_productivity_fail_invalid_data_group(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "0", "group": "Next" * 51},
        )
        response = create_productivity(request)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_index_fail_get(self) -> None:
        request = RequestFactory().get("productivity/")
        response = index(request)

        self.assertEqual(response.status_code, 405)
        self.assertDictEqual(
            json.loads(response.content),
            {"error": "Request method not allowed"},
        )


# pylint: disable-next=invalid-name
def tearDownModule() -> None:
    log_filename = LOGGING["handlers"]["file"]["filename"]
    try:
        Path(log_filename).unlink()
        print(f"Removed {log_filename}")
    except PermissionError:
        print(f"{log_filename} not removed")
