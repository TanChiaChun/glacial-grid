"""Models for productivity app."""

import logging
from datetime import datetime

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
