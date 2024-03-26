import json
import logging
from datetime import date, datetime, time
from pathlib import Path

from django.core.exceptions import ValidationError
from django.http import QueryDict
from django.test import RequestFactory, TestCase

# pylint: disable=wrong-import-order
from mysite.settings import LOGGING
from productivity.models import Productivity, logger
from productivity.views import (
    create_productivity,
    get_productivities,
    get_productivity_object,
    index,
    index_detail,
    update_productivity,
)

# pylint: enable=wrong-import-order


def is_productivity_almost_equal(
    first: Productivity, second: Productivity
) -> bool:
    """Compare Productivity objects and check if they are almost equal.

    - `id` attribute is only compared if not `None`.
    - `last_check` and `last_check_undo` attributes are only compared for date.

    Args:
        first:
            Productivity object to be compared.
        second:
            Productivity object to be compared against.

    Returns:
        True if Productivity object is almost equal, False otherwise.
    """
    return (
        ((first.id == second.id) if (first.id is not None) else True)
        and (first.item == second.item)
        and (first.frequency == second.frequency)
        and (first.group == second.group)
        and (first.last_check.date() == second.last_check.date())
        and (first.last_check_undo.date() == second.last_check_undo.date())
    )


def reset_last_check_time(json_objs: list[dict[str, str]]) -> None:
    """Reset time of each `last_check`'s & `last_check_undo`'s value.

    Args:
        json_objs:
            List of serialized Productivity models.

    Raises:
        KeyError:
            Key not found.
    """
    for j in json_objs:
        j["last_check"] = j["last_check"][0:11] + "00:00:00"
        j["last_check_undo"] = j["last_check_undo"][0:11] + "00:00:00"


class ProductivityModelTests(TestCase):
    def setUp(self) -> None:
        self.dt_today = datetime.combine(date.today(), time())
        self.productivity = Productivity(
            item="Calendar",
            frequency=0,
            group="Next",
        )

    def test_deserialize_json(self) -> None:
        j = {
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": self.dt_today.isoformat(),
            "last_check_undo": "0001-01-01T00:00:00",
        }
        productivity = Productivity.deserialize_json(j)

        self.productivity.last_check = self.dt_today
        self.assertIs(
            is_productivity_almost_equal(productivity, self.productivity), True
        )

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
        self.productivity.last_check = self.dt_today
        self.assertEqual(
            str(self.productivity),
            f"[Key-Next] Calendar ({self.dt_today.strftime('%d %b %I:%M %p')})",
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

    def test_save_new_object(self) -> None:
        self.productivity.save()

        self.assertEqual(Productivity.objects.count(), 1)
        self.assertEqual(self.productivity.last_check_undo, datetime.min)

    def test_save_existing_object(self) -> None:
        self.productivity.last_check = self.dt_today
        self.productivity.save()

        self.assertEqual(Productivity.objects.count(), 1)
        self.assertEqual(self.productivity.last_check_undo, self.dt_today)

    def test_save_invalid_data(self) -> None:
        self.productivity.frequency = 10

        with self.assertRaises(ValidationError) as cm:
            self.productivity.save()
        self.assertIn("frequency", cm.exception.args[0])

        self.assertEqual(Productivity.objects.count(), 0)

    def test_serialize_json(self) -> None:
        self.productivity.id = 1
        self.productivity.last_check = self.dt_today
        expected = {
            "id": "1",
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": self.dt_today.isoformat(),
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
        expected = Productivity(
            id=1,
            item="Calendar",
            frequency=0,
            group="Next",
            last_check=self.dt_today,
        )
        self.assertIs(
            is_productivity_almost_equal(productivities[0], expected), True
        )

        self.productivity.item = "To-Do"
        self.productivity.save()
        productivities = Productivity.objects.all()
        self.assertEqual(len(productivities), 1)
        expected = Productivity(
            id=1,
            item="To-Do",
            frequency=0,
            group="Next",
            last_check=self.dt_today,
            last_check_undo=self.dt_today,
        )
        self.assertIs(
            is_productivity_almost_equal(productivities[0], expected), True
        )

        self.assertEqual(
            self.productivity.delete(), (1, {"productivity.Productivity": 1})
        )
        self.assertEqual(Productivity.objects.count(), 0)


class ViewsTest(TestCase):
    def setUp(self) -> None:
        self.dt_today = datetime.combine(date.today(), time())
        self.productivity = Productivity(
            item="Calendar",
            frequency=0,
            group="Next",
        )

    def test_create_productivity(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "0", "group": "Next"},
        )
        response = create_productivity(request.POST)

        self.assertEqual(response.status_code, 201)

        j = json.loads(response.content)
        self.assertEqual(len(j), 6)
        self.assertIn("id", j)

        self.productivity.last_check = self.dt_today
        self.assertIs(
            is_productivity_almost_equal(
                Productivity.deserialize_json(j), self.productivity
            ),
            True,
        )

        self.assertEqual(Productivity.objects.count(), 1)

    def test_create_productivity_fail_missing_data(self) -> None:
        request = RequestFactory().post("productivity/")
        response = create_productivity(request.POST)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Missing data"}
        )

    def test_create_productivity_fail_invalid_data_item(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar" * 26, "frequency": "0", "group": "Next"},
        )
        response = create_productivity(request.POST)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_create_productivity_fail_invalid_data_frequency(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "10", "group": "Next"},
        )
        response = create_productivity(request.POST)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_create_productivity_fail_invalid_data_group(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "0", "group": "Next" * 51},
        )
        response = create_productivity(request.POST)

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Data validation error"}
        )

    def test_get_productivity_object(self) -> None:
        self.productivity.save()

        expected = Productivity(
            id=1,
            item="Calendar",
            frequency=0,
            group="Next",
            last_check=self.dt_today,
        )
        self.assertIs(
            is_productivity_almost_equal(get_productivity_object(1), expected),
            True,
        )

    def test_get_productivity_not_exist(self) -> None:
        with self.assertRaises(Productivity.DoesNotExist):
            get_productivity_object(1)

    def test_get_productivities_zero_object(self) -> None:
        response = get_productivities()

        self.assertEqual(response.status_code, 200)

        self.assertListEqual(json.loads(response.content), [])

    def test_get_productivities_one_object(self) -> None:
        self.productivity.save()

        response = get_productivities()

        self.assertEqual(response.status_code, 200)

        expected = [
            {
                "id": "1",
                "item": "Calendar",
                "frequency": "Key",
                "group": "Next",
                "last_check": self.dt_today.isoformat(),
                "last_check_undo": "0001-01-01T00:00:00",
            }
        ]
        productivities = json.loads(response.content)
        reset_last_check_time(productivities)
        self.assertListEqual(productivities, expected)

    def test_index_get(self) -> None:
        self.productivity.save()
        Productivity(item="To-Do", frequency=0, group="Next").save()

        request = RequestFactory().get("productivity/")
        response = index(request)

        self.assertEqual(response.status_code, 200)

        expected = [
            {
                "id": "1",
                "item": "Calendar",
                "frequency": "Key",
                "group": "Next",
                "last_check": self.dt_today.isoformat(),
                "last_check_undo": "0001-01-01T00:00:00",
            },
            {
                "id": "2",
                "item": "To-Do",
                "frequency": "Key",
                "group": "Next",
                "last_check": self.dt_today.isoformat(),
                "last_check_undo": "0001-01-01T00:00:00",
            },
        ]
        productivities = json.loads(response.content)
        reset_last_check_time(productivities)
        self.assertListEqual(productivities, expected)

    def test_index_post(self) -> None:
        request = RequestFactory().post(
            "productivity/",
            data={"item": "Calendar", "frequency": "0", "group": "Next"},
        )
        response = index(request)

        self.assertEqual(response.status_code, 201)

        self.productivity.last_check = self.dt_today
        self.assertIs(
            is_productivity_almost_equal(
                Productivity.deserialize_json(json.loads(response.content)),
                self.productivity,
            ),
            True,
        )

    def test_index_fail_put(self) -> None:
        request = RequestFactory().put("productivity/")
        response = index(request)

        self.assertEqual(response.status_code, 405)

    def test_index_detail_get(self) -> None:
        self.productivity.save()

        request = RequestFactory().get("productivity/1/")
        response = index_detail(request, 1)

        self.assertEqual(response.status_code, 200)

        expected = {
            "id": "1",
            "item": "Calendar",
            "frequency": "Key",
            "group": "Next",
            "last_check": self.dt_today.isoformat(),
            "last_check_undo": "0001-01-01T00:00:00",
        }
        productivity = json.loads(response.content)
        reset_last_check_time([productivity])
        self.assertDictEqual(productivity, expected)

    def test_index_detail_get_not_exist(self) -> None:
        request = RequestFactory().get("productivity/1/")
        response = index_detail(request, 1)

        self.assertEqual(response.status_code, 404)

        self.assertDictEqual(
            json.loads(response.content), {"error": "ID not found"}
        )

    def test_index_detail_fail_post(self) -> None:
        request = RequestFactory().post("productivity/1/")
        response = index_detail(request, 1)

        self.assertEqual(response.status_code, 405)

    def test_update_productivity_auto_last_check(self) -> None:
        self.productivity.save()

        response = update_productivity(
            self.productivity,
            QueryDict("item=To-Do&frequency=1&group=Next1&last_check="),
        )

        self.assertEqual(response.status_code, 200)

        expected = {
            "id": "1",
            "item": "To-Do",
            "frequency": "Loop",
            "group": "Next1",
            "last_check": self.dt_today.isoformat(),
            "last_check_undo": self.dt_today.isoformat(),
        }
        productivity = json.loads(response.content)
        reset_last_check_time([productivity])
        self.assertDictEqual(productivity, expected)

    def test_update_productivity_manual_last_check(self) -> None:
        self.productivity.save()

        response = update_productivity(
            self.productivity,
            QueryDict(
                (
                    "item=To-Do&frequency=1&group=Next1&"
                    "last_check=2024-03-25T00%3A00%3A00"
                )
            ),
        )

        self.assertEqual(response.status_code, 200)

        expected = {
            "id": "1",
            "item": "To-Do",
            "frequency": "Loop",
            "group": "Next1",
            "last_check": datetime(2024, 3, 25).isoformat(),
            "last_check_undo": self.dt_today.isoformat(),
        }
        productivity = json.loads(response.content)
        reset_last_check_time([productivity])
        self.assertDictEqual(productivity, expected)

    def test_update_productivity_fail_missing_data(self) -> None:
        self.productivity.save()

        response = update_productivity(self.productivity, QueryDict(""))

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content), {"error": "Missing data"}
        )

    def test_update_productivity_fail_invalid_last_check(self) -> None:
        self.productivity.save()

        response = update_productivity(
            self.productivity,
            QueryDict("item=To-Do&frequency=1&group=Next1&last_check=a"),
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content),
            {"error": "Invalid data for last_check"},
        )

    def test_update_productivity_fail_data_validation(self) -> None:
        self.productivity.save()

        response = update_productivity(
            self.productivity,
            QueryDict("item=To-Do&frequency=10&group=Next1&last_check="),
        )

        self.assertEqual(response.status_code, 400)
        self.assertDictEqual(
            json.loads(response.content),
            {"error": "Data validation error"},
        )


# pylint: disable-next=invalid-name
def tearDownModule() -> None:
    log_filename = LOGGING["handlers"]["file"]["filename"]
    try:
        Path(log_filename).unlink()
        print(f"Removed {log_filename}")
    except PermissionError:
        print(f"{log_filename} not removed")
