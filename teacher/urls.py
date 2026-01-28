from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views


app_name = "teacher"

urlpatterns = [
    path("teacher_login/", views.index, name="teacher_login"),
    path("teacher_dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
]
