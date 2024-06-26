"""URL configuration for productivity app."""

from django.urls import path

from productivity import views

urlpatterns = [
    path("", views.index),
    path("<int:productivity_id>/", views.index_detail),
]
