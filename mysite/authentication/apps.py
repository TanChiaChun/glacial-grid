"""Application configuration."""

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    """Application configuration objects, metadata for an application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"
