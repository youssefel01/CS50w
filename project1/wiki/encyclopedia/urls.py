from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/create/", views.create, name="create"),
    path("wiki/<str:title>/", views.getEntry, name="entry"),
    path("wiki/<str:title>/edit/", views.editEntry, name="edit"),
    path("wiki/random", views.randomEntry, name="random"),
    path("wiki/", views.searchEntry, name="search"),
]
