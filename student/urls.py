from django.urls import path

from . import views

# This namespace is useful so you can refer to urls as 'student:translator'
app_name = "student"

urlpatterns = [
    # This maps 'http://127.0.0.1:8000/student/translator/' to your view
    path("translator/", views.translator_view, name="translator"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
]
