from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("create-listing", views.CreateListing, name="CreateListing"),
    path("Watchlist", views.Watchlist, name="Watchlist"),

    path("listing-page/<str:pk>/", views.listingPage, name="listingPage"),
    path("listing-comment/<str:pk>/", views.listingComment, name="listingComment"),
]


