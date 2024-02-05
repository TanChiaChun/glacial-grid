"""Application configuration."""

from django.apps import AppConfig


class ProductivityConfig(AppConfig):
    """Application configuration objects, metadata for an application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "productivity"
