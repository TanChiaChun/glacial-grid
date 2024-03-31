"""URL configuration for authentication app."""

from django.urls import path

from authentication import views

urlpatterns = [
    path("csrftoken/", views.csrftoken),
    path("login/", views.authentication_login),
]
