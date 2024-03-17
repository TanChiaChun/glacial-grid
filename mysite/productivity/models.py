"""Models for productivity app."""

import logging
from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models

logger = logging.getLogger(__name__)


class Productivity(models.Model):
    """Productivity model."""

    class Frequency(models.IntegerChoices):
        """Choices for Frequency field."""

        KEY = 0
        LOOP = 1
        DAY = 2
        WEEK = 3
        MONTH = 4

    item = models.CharField(max_length=200)
    frequency = models.IntegerField(choices=Frequency.choices)
    group = models.CharField(max_length=200)
    last_check = models.DateTimeField(auto_now=True)
    last_check_undo = models.DateTimeField(default=datetime.min)

    @classmethod
    def deserialize_json(cls, json_obj: dict[str, str]) -> "Productivity":
        """Deserialize JSON to model.

        Args:
            json_obj:
                JSON object to deserialize.

        Returns:
            Model instance.

        Raises:
            KeyError:
                JSON object does not has the required key.
            django.core.exceptions.ValidationError:
                Model field fail validation.
        """
        frequency_name = json_obj["frequency"].upper()
        try:
            frequency = cls.Frequency[frequency_name].value
        except KeyError as exc:
            raise ValidationError("Invalid enum name for Frequency") from exc

        productivity = cls(
            item=json_obj["item"],
            frequency=frequency,
            group=json_obj["group"],
            last_check=cls.parse_iso_datetime(
                json_obj["last_check"], "last_check"
            ),
            last_check_undo=cls.parse_iso_datetime(
                json_obj["last_check_undo"], "last_check_undo"
            ),
        )
        productivity.clean_fields()

        return productivity

    @classmethod
    def parse_iso_datetime(cls, dt_iso: str, field_name: str) -> datetime:
        """Parse datetime string in ISO format into a datetime object.

        Args:
            dt_iso:
                Datetime string in ISO format.
            field_name:
                Model field name to be displayed in exception message.

        Returns:
            Datetime object.

        Raises:
            django.core.exceptions.ValidationError:
                Invalid datetime string format.
        """
        try:
            dt = datetime.fromisoformat(dt_iso)
        except ValueError as exc:
            raise ValidationError(
                f"Invalid date_string format for {field_name}"
            ) from exc

        return dt

    def __str__(self) -> str:
        last_check = (
            self.last_check.strftime("%d %b %I:%M %p")
            if self.last_check
            else ""
        )

        return (
            f"[{self.get_frequency()}-{self.group}]"
            + " "
            + self.item
            + " "
            + f"({last_check})"
        )

    def get_frequency(self) -> str:
        """Return name of Frequency enum in title case."""
        frequency_name = ""

        try:
            frequency_name = self.Frequency(self.frequency).name.title()
        except ValueError:
            logger.error("Invalid enum value for Frequency")

        return frequency_name

    def serialize_json(self) -> dict[str, str]:
        """Serialize model to JSON.

        Returns:
            Dictionary mapping of serialized model in JSON.
        """
        return {
            "id": str(self.id),
            "item": self.item,
            "frequency": self.get_frequency(),
            "group": self.group,
            "last_check": (
                self.last_check.isoformat() if self.last_check else ""
            ),
            "last_check_undo": self.last_check_undo.isoformat(),
        }
