"""URL configuration for productivity app."""

from django.urls import path

from productivity import views

urlpatterns = [path("create/", views.create)]
