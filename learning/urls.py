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
    
    # --- CRUD CREATE ---
    path("manage/theme/", views.add_theme, name="add_theme"),
    path("manage/section/", views.add_section, name="add_section"),
    path("manage/word/", views.upload_word, name="upload_word"),

    # --- CRUD UPDATE (EDIT) ---
    path("manage/theme/<int:pk>/edit/", views.edit_theme, name="edit_theme"),
    path("manage/section/<int:pk>/edit/", views.edit_section, name="edit_section"),
    path("manage/word/<int:pk>/edit/", views.edit_word, name="edit_word"),

    # --- CRUD DELETE ---
    path("manage/theme/<int:pk>/delete/", views.delete_theme, name="delete_theme"),
    path("manage/section/<int:pk>/delete/", views.delete_section, name="delete_section"),
    path("manage/word/<int:pk>/delete/", views.delete_word, name="delete_word"),

    # --- STORIES & QUIZZES ---
    path("quiz_select/", views.quiz_select, name="quiz_select"),
    path("stories/<int:story_id>/", views.story_view, name="story_view"),
    path('quizzes/', views.manage_quizzes, name='manage_quizzes'),
    path('quizzes/create/', views.create_quiz, name='create_quiz'),
    path('quizzes/delete/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path("puzzles/", views.sentence_quiz_list, name="quiz_list"),
    path("puzzles/<int:quiz_id>/", views.take_sentence_quiz, name="take_quiz"),
    path("manage/story/add/", views.add_story, name="add_story"),
    
    # -> NEW MATH QUIZ ROUTE <-
    path("math-magic/", views.math_quiz, name="math_quiz"),

    # --- STORY QUIZ CRUD ---
    # Notice the add route needs the story_id so it knows which story to attach the quiz to
    path("manage/story/<int:story_id>/question/add/", views.add_question, name="add_question"),
    path("manage/question/<int:pk>/edit/", views.edit_question, name="edit_question"),
    path("manage/question/<int:pk>/delete/", views.delete_question, name="delete_question"),
    path("manage/story/<int:pk>/edit/", views.edit_story, name="edit_story"),
    path("manage/story/<int:pk>/delete/", views.delete_story, name="delete_story"),
    path('story_library/', views.story_library, name='story_library'),

    # --- VOCAB QUIZ ---
    path("manage/vocab-quizzes/", views.manage_vocab_quizzes, name="manage_vocab_quizzes"),
    path("api/vocab-quiz/toggle/<int:section_id>/", views.toggle_vocab_quiz, name="toggle_vocab_quiz"),
    path("vocab_quizzes/", views.vocab_quiz_list, name="vocab_quiz_list"),
    path("vocab_quiz/<int:quiz_id>/", views.take_vocab_quiz, name="take_vocab_quiz"),
]