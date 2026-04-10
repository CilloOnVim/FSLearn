from django.urls import path

from . import views

# This namespace is useful so you can refer to urls as 'student:translator'
app_name = "student"

urlpatterns = [
    # This maps 'http://127.0.0.1:8000/student/translator/' to your view
    path("translator/", views.translator_view, name="translator"),
    path("restructure/", views.restructure_sentence_view, name="restructure"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    path("api/word/<int:word_id>/done/", views.mark_word_done, name="mark_word_done"),
    path("api/quiz/<int:quiz_id>/save/", views.save_quiz_score, name="save_quiz_score"),
    path("api/story-quiz/<int:story_id>/save/", views.save_story_quiz_score, name="save_story_quiz_score"),
    path("api/vocab-quiz/<int:quiz_id>/save/", views.save_vocab_quiz_score, name="save_vocab_quiz_score"),
]
