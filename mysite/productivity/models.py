"""Models for productivity app."""

from datetime import datetime

from django.db import models


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
