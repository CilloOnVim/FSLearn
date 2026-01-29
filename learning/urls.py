from django.urls import path

from . import views

app_name = "learning"  # <--- Namespace is CRITICAL

urlpatterns = [
    # 1. Theme List (The Main Menu)
    path("", views.theme_list, name="theme_list"),
    # 2. Section List (Inside a Theme)
    path("theme/<int:theme_id>/", views.section_list, name="section_list"),
    # 3. Word List (Inside a Section)
    path("section/<int:section_id>/", views.word_list, name="word_list"),
    # 4. The Lesson Page (The actual content)
    path("word/<slug:word_slug>/", views.word_detail, name="word_detail"),
    path("manage/", views.manage_content, name="manage_content"),
    path("manage/theme/", views.add_theme, name="add_theme"),
    path("manage/section/", views.add_section, name="add_section"),
    # Note: You can rename 'upload_word' to 'add_word' to be consistent if you want
    path("manage/word/", views.upload_word, name="upload_word"),
]
