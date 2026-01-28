from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name="core"

urlpatterns = [
    path("", views.index, name="index"),  # Empty string means root domain
    path("login/", views.login_view, name="login"),
]
