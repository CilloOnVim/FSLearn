from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from .models import Theme, Section, Word, Story, QuizQuestion, QuizChoice, SentenceQuiz

# --- INLINES (For editing child objects inside the parent page) ---
class SectionInline(TabularInline):
    model = Section
    extra = 1 # Shows 1 empty row by default

class QuizQuestionInline(TabularInline):
    model = QuizQuestion
    extra = 1

class QuizChoiceInline(TabularInline):
    model = QuizChoice
    extra = 2

# --- MODEL ADMINS ---
@admin.register(Theme)
class ThemeAdmin(ModelAdmin):
    list_display = ('title', 'order')
    search_fields = ('title',)
    inlines = [SectionInline] # Edits Sections inside the Theme page

@admin.register(Word)
class WordAdmin(ModelAdmin):
    list_display = ('name', 'section', 'order')
    list_filter = ('section__theme', 'section') # Adds a clean sidebar filter
    search_fields = ('name',)
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Story)
class StoryAdmin(ModelAdmin):
    list_display = ('title', 'theme')
    list_filter = ('theme',)
    search_fields = ('title',)
    inlines = [QuizQuestionInline]

@admin.register(QuizQuestion)
class QuizQuestionAdmin(ModelAdmin):
    list_display = ('text', 'story')
    inlines = [QuizChoiceInline] # Edits Choices inside the Question page

@admin.register(SentenceQuiz)
class SentenceQuizAdmin(ModelAdmin):
    list_display = ('original_text', 'created_at')

# We hide Section and QuizChoice from the main menu since they are handled via Inlines
admin.site.register(Section, ModelAdmin)
admin.site.register(QuizChoice, ModelAdmin)