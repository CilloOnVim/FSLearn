from re import A

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SectionForm, ThemeForm, WordForm
from .models import Section, Theme, Word

# Create your views here.


# 1. THEME LIST
def theme_list(request):
    themes = Theme.objects.all()
    return render(request, "learning/theme_list.html", {"themes": themes})


# 2. SECTION LIST
def section_list(request, theme_id):
    theme = get_object_or_404(Theme, id=theme_id)
    sections = theme.sections.all()  # Uses the 'related_name' from models.py
    return render(
        request, "learning/section_list.html", {"theme": theme, "sections": sections}
    )


# 3. WORD LIST
def word_list(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    words = section.words.all()
    return render(
        request, "learning/word_list.html", {"section": section, "words": words}
    )


# 4. WORD DETAIL (The Lesson Player)
def word_detail(request, word_slug):
    word = get_object_or_404(Word, slug=word_slug)

    # Logic for "Next" and "Previous" buttons
    # We find neighbors by ordering
    section_words = list(word.section.words.all())
    current_index = section_words.index(word)

    previous_word = section_words[current_index - 1] if current_index > 0 else None
    next_word = (
        section_words[current_index + 1]
        if current_index < len(section_words) - 1
        else None
    )

    return render(
        request,
        "learning/word_detail.html",
        {"word": word, "previous_word": previous_word, "next_word": next_word},
    )


# THE HUB (The Menu Page)
@login_required
def manage_content(request):
    # Check if teacher
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")
    return render(request, "learning/manage_content.html")


# 1. ADD WORD
@login_required
def upload_word(request):
    # Security Check: Kick them out if they aren't a teacher
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    if request.method == "POST":
        # request.FILES is required to handle video/image uploads!
        form = WordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Redirect back to dashboard or show a success message
            return redirect("teacher:teacher_dashboard")
    else:
        form = WordForm()

    return render(request, "learning/upload_word.html", {"form": form})


# 2. ADD THEME
@login_required
def add_theme(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    if request.method == "POST":
        form = ThemeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("learning:manage_content")
    else:
        form = ThemeForm()
    return render(request, "learning/upload_theme.html", {"form": form})


# 3. ADD SECTION
@login_required
def add_section(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("learning:manage_content")
    else:
        form = SectionForm()
    return render(request, "learning/upload_section.html", {"form": form})
