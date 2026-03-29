from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from learning import views as learning_views


app_name = "teacher"

urlpatterns = [
    path("teacher_login/", views.index, name="teacher_login"),
    path("teacher_dashboard/", views.teacher_dashboard, name="teacher_dashboard"),

    # --- UPDATE (EDIT) PATHS ---
    path("manage/theme/<int:pk>/edit/", learning_views.edit_theme, name="edit_theme"),
    path("manage/section/<int:pk>/edit/", learning_views.edit_section, name="edit_section"),
    path("manage/word/<int:pk>/edit/", learning_views.edit_word, name="edit_word"),

    # --- DELETE PATHS ---
    path("manage/theme/<int:pk>/delete/", learning_views.delete_theme, name="delete_theme"),
    path("manage/section/<int:pk>/delete/", learning_views.delete_section, name="delete_section"),
    path("manage/word/<int:pk>/delete/", learning_views.delete_word, name="delete_word"),
    path("class_progress/", views.class_progress_report, name="class_progress_report"),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('my-students/', views.my_students, name='my_students'),
    path('my-students/remove/<int:student_id>/', views.remove_student, name='remove_student'),
]
