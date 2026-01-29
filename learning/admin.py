from django.contrib import admin

from .models import Section, Theme, Word

# Register your models here.


# 1. Setup for Words inside Section
class WordInline(admin.TabularInline):
    model = Word
    extra = 1  # Shows one empty row by default
    fields = ("name", "slug", "video", "image", "order")  # Quick entry fields
    prepopulated_fields = {"slug": ("name",)}  # Auto-fills slug as you type!


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("title", "theme", "order")
    list_filter = ("theme",)  # Adds a sidebar filter by Theme
    search_fields = ("title",)
    inlines = [WordInline]  # THIS is the magic line. Adds words inside Section.


# 2. Setup for Sections inside Theme
class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ("title", "order")


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    inlines = [SectionInline]  # Adds sections inside Theme.


# 3. Register Word separately in case you need to edit just one
@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "order")
    search_fields = ("name", "description")
    list_filter = ("section__theme", "section")  # Filter by Theme AND Section
    prepopulated_fields = {"slug": ("name",)}
