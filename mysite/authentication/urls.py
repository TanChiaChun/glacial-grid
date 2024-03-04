"""URL configuration for authentication app."""

from django.urls import path

from authentication import views

urlpatterns = [path("csrftoken/", views.acquire_csrf_token)]
