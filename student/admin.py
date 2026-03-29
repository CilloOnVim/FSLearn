from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import FSLSign, FSLWord, StudentProfile, WordProgress, QuizProgress, StoryQuizProgress

@admin.register(StudentProfile)
class StudentProfileAdmin(ModelAdmin):
    list_display = ('nickname', 'level', 'section', 'guardian_name')
    list_filter = ('level', 'section')
    search_fields = ('nickname', 'guardian_name', 'user__username')
    
    # Groups the inputs into clean, visual cards
    fieldsets = (
        ("Account Link", {"fields": ("user",)}),
        ("Student Details", {"fields": ("nickname", "avatar")}),
        ("Enrollment Info", {"fields": ("level", "section")}),
        ("Guardian Info", {"fields": ("guardian_name",)}),
    )

@admin.register(WordProgress)
class WordProgressAdmin(ModelAdmin):
    list_display = ('student', 'word', 'completed_at')
    list_filter = ('student__level',)
    search_fields = ('student__nickname', 'word__name')

@admin.register(StoryQuizProgress)
class StoryQuizProgressAdmin(ModelAdmin):
    list_display = ('student', 'story', 'score', 'is_passed')
    list_filter = ('is_passed',)

# Simple registers for the rest
admin.site.register(FSLSign, ModelAdmin)
admin.site.register(FSLWord, ModelAdmin)
admin.site.register(QuizProgress, ModelAdmin)