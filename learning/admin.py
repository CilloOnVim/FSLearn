from django.contrib import admin
from .models import Section, Theme, Word, Story, QuizQuestion, QuizChoice

# ==========================================
# 1. DICTIONARY SETUP (Existing Features)
# ==========================================

# Setup for Words inside Section
class WordInline(admin.TabularInline):
    model = Word
    extra = 1
    fields = ("name", "slug", "video", "image", "order")
    prepopulated_fields = {"slug": ("name",)}

# Setup for Sections inside Theme
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ("title", "order")

@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    inlines = [SectionInline]

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "order")
    list_filter = ("theme",)
    search_fields = ("title",)
    inlines = [WordInline]

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "order")
    search_fields = ("name", "description")
    list_filter = ("section__theme", "section")
    prepopulated_fields = {"slug": ("name",)}


# ==========================================
# 2. STORY & QUIZ SETUP (New Features)
# ==========================================

# A. Choices Inline (The Answer Slots)
# This puts the 4 answer slots inside the Question page
class QuizChoiceInline(admin.TabularInline):
    model = QuizChoice
    extra = 4       # Automatically shows 4 blank slots
    min_num = 2     # Forces at least 2 choices
    fields = ('text', 'is_correct', 'image')

# B. Question Admin (The Question Creator)
@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'story', 'video')
    list_filter = ('story',)
    search_fields = ('text', 'story__title')
    inlines = [QuizChoiceInline] # <--- CRITICAL: Adds choices to the Question page

# C. Question Inline (Optional: See questions inside the Story page)
class QuizQuestionInline(admin.StackedInline):
    model = QuizQuestion
    extra = 0
    show_change_link = True # Adds a button to jump to the full Question edit page

# D. Story Admin (The Main Container)
@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme')
    list_filter = ('theme',)
    search_fields = ('title',)
    inlines = [QuizQuestionInline] # Shows list of questions attached to this story