import json
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from .forms import SectionForm, ThemeForm, WordForm, StoryForm, QuizQuestionForm, ChoiceFormSet
from .models import Section, Theme, Word, SentenceQuiz, QuizQuestion, Story
from student.models import FSLWord
from student.nlp_utils import translate_to_fsl


# 1. THEME LIST
def theme_list(request):
    themes = Theme.objects.all()
    return render(request, "learning/theme_list.html", {"themes": themes})


# 2. SECTION LIST
def section_list(request, theme_id):
    theme = get_object_or_404(Theme, pk=theme_id)
    sections = theme.sections.all()  
    return render(
        request, "learning/section_list.html", {"theme": theme, "sections": sections}
    )


# 3. WORD LIST
def word_list(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    words = section.words.all()
    return render(
        request, "learning/word_list.html", {"section": section, "words": words}
    )


# 4. WORD DETAIL (The Lesson Player)
def word_detail(request, word_slug):
    word = get_object_or_404(Word, slug=word_slug)

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
    if not hasattr(request.user, "teacher_profile"):
        return redirect("learning:story_list")
    
    themes = Theme.objects.prefetch_related('sections__words').all()
    return render(request, "learning/manage_content.html", {
        "themes": themes
    })


# 1. ADD WORD
@login_required
def upload_word(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    if request.method == "POST":
        form = WordForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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


# 5. STORY LIST (Pick a story)
@login_required
def story_list(request):
    stories = Story.objects.all()
    return render(request, "learning/story_list.html", {"stories": stories})


# 6. STORY PLAYER & QUIZ (The logic)
def story_view(request, story_id):
    story = get_object_or_404(Story, pk=story_id)
    
    questions_data = []
    questions = story.questions.all()
    
    for q in questions:
        if not q.video:
            continue

        choices = []
        for c in q.choices.all():
            choices.append({
                "text": c.text,
                "image": c.image.url if c.image else None,
                "is_correct": c.is_correct
            })
            
        questions_data.append({
            "video_url": q.video.url, 
            "text": q.text,
            "choices": choices
        })

    context = {
        "story": story,
        "quiz_data_json": json.dumps(questions_data, cls=DjangoJSONEncoder)
    }
    return render(request, "learning/story_detail.html", context)


# 7. MANAGE QUIZZES (The List)
@login_required
def manage_quizzes(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")
    
    quizzes = SentenceQuiz.objects.all().order_by('-created_at')
    return render(request, "learning/manage_quizzes.html", {"quizzes": quizzes})

# 8. CREATE QUIZ (The Magic Builder)
@login_required
def create_quiz(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    context = {}

    if request.method == "POST":
        sentence = request.POST.get("sentence", "").strip()
        action = request.POST.get("action") 

        if sentence:
            # Import your new helper at the top of the file if you haven't already:
            from student.nlp_utils import validate_quiz_sentence
            
            # ONE CLEAN CALL. The view acts as a traffic cop, not a database worker.
            validation_data = validate_quiz_sentence(sentence)

            context = {
                "original": sentence,
                "nlp_result": validation_data["nlp_result"],
                "report": validation_data["report"],
                "all_good": validation_data["all_good"]
            }

            if action == "save":
                SentenceQuiz.objects.create(
                    original_text=sentence,
                    structure_json=validation_data["nlp_result"]
                )
                messages.success(request, "Quiz saved successfully!")
                return redirect("learning:manage_quizzes")

    return render(request, "learning/create_quiz.html", context)


# ... (Skip down to your take_sentence_quiz view) ...


@login_required
def take_sentence_quiz(request, quiz_id):
    """The actual drag-and-drop player"""
    quiz = get_object_or_404(SentenceQuiz, pk=quiz_id)
    structure = quiz.structure_json

    correct_sequence = []
    tiles = []

    def process_category(text_block, category_name):
        if not text_block: 
            return
            
        words = text_block.split()
        for word in words:
            clean_word = word.strip(".,!?")
            if not clean_word: 
                continue

            # 1. Fingerspelling logic
            if clean_word.startswith("fs-"):
                display_word = clean_word.replace("fs-", "")
                video_url = None 
                
            # 2. NEW: Name logic so the tiles render names correctly
            elif clean_word.startswith("name-"):
                display_word = clean_word.replace("name-", "").replace("_", " ")
                word_obj = FSLWord.objects.filter(word__iexact=display_word).first()
                video_url = word_obj.video.url if word_obj and word_obj.video else None
                
            # 3. Standard Vocabulary
            else:
                display_word = clean_word
                word_obj = FSLWord.objects.filter(word__iexact=clean_word).first()
                video_url = word_obj.video.url if word_obj and word_obj.video else None

            tiles.append({
                "word": display_word,
                "category": category_name, 
                "video_url": video_url
            })
            
            correct_sequence.append(display_word)

    # CRITICAL ORDERING FOR DOM CHECK: Time -> Subject -> Action -> Topic
    process_category(structure.get('time'), 'time')
    process_category(structure.get('comment_subject'), 'subject') 
    process_category(structure.get('comment_verb'), 'action')     
    process_category(structure.get('topic'), 'topic')

    shuffled_tiles = list(tiles)
    random.shuffle(shuffled_tiles)

    context = {
        "quiz": quiz,
        "shuffled_tiles": shuffled_tiles,
        "correct_sequence_json": json.dumps(correct_sequence) 
    }
    
    return render(request, "learning/take_quiz.html", context)

# 9. DELETE QUIZ
@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(SentenceQuiz, pk=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect("learning:manage_quizzes")


@login_required
def sentence_quiz_list(request):
    quizzes = SentenceQuiz.objects.all().order_by('-created_at')
    
    passed_quiz_ids = []
    if hasattr(request.user, 'student_profile'):
        passed_quiz_ids = request.user.student_profile.quiz_scores.filter(
            is_passed=True
        ).values_list('quiz_id', flat=True)

    return render(request, "learning/quiz_list.html", {
        "quizzes": quizzes,
        "passed_quiz_ids": passed_quiz_ids
    })

@login_required
def take_sentence_quiz(request, quiz_id):
    """The actual drag-and-drop player"""
    quiz = get_object_or_404(SentenceQuiz, pk=quiz_id)
    structure = quiz.structure_json

    correct_sequence = []
    tiles = []

    def process_category(text_block, category_name):
        if not text_block: 
            return
            
        words = text_block.split()
        for word in words:
            clean_word = word.strip(".,!?")
            if not clean_word: 
                continue

            # 1. Fingerspelling logic
            if clean_word.startswith("fs-"):
                display_word = clean_word.replace("fs-", "")
                video_url = None 
                
            # --- THE FIX YOU MISSED: Name logic so the tiles render names correctly ---
            elif clean_word.startswith("name-"):
                display_word = clean_word.replace("name-", "").replace("_", " ")
                word_obj = FSLWord.objects.filter(word__iexact=display_word).first()
                video_url = word_obj.video.url if word_obj and word_obj.video else None
            # --------------------------------------------------------------------------
            
            # 3. Standard Vocabulary
            else:
                display_word = clean_word
                word_obj = FSLWord.objects.filter(word__iexact=clean_word).first()
                video_url = word_obj.video.url if word_obj and word_obj.video else None

            tiles.append({
                "word": display_word,
                "category": category_name, 
                "video_url": video_url
            })
            
            correct_sequence.append(display_word)

    # CRITICAL ORDERING FOR DOM CHECK: Time -> Subject -> Action -> Topic
    process_category(structure.get('time'), 'time')
    process_category(structure.get('comment_subject'), 'subject') 
    process_category(structure.get('comment_verb'), 'action')     
    process_category(structure.get('topic'), 'topic')

    shuffled_tiles = list(tiles)
    random.shuffle(shuffled_tiles)

    context = {
        "quiz": quiz,
        "shuffled_tiles": shuffled_tiles,
        "correct_sequence_json": json.dumps(correct_sequence) 
    }
    
    return render(request, "learning/take_quiz.html", context)

# ==========================================
# --- UPDATE (EDIT) VIEWS ---
# ==========================================

@login_required
def edit_theme(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    theme = get_object_or_404(Theme, pk=pk)
    
    if request.method == "POST":
        form = ThemeForm(request.POST, request.FILES, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, "Theme updated successfully.")
            return redirect("learning:manage_content")
    else:
        form = ThemeForm(instance=theme)
        
    return render(request, "learning/upload_theme.html", {"form": form, "is_edit": True})

@login_required
def edit_section(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    section = get_object_or_404(Section, pk=pk)
    
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated.")
            return redirect("learning:manage_content")
    else:
        form = SectionForm(instance=section)
    return render(request, "learning/upload_section.html", {"form": form, "is_edit": True})

@login_required
def edit_word(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    word = get_object_or_404(Word, pk=pk)
    
    if request.method == "POST":
        form = WordForm(request.POST, request.FILES, instance=word)
        if form.is_valid():
            form.save()
            messages.success(request, "Word updated.")
            return redirect("learning:manage_content")
    else:
        form = WordForm(instance=word)
    return render(request, "learning/upload_word.html", {"form": form, "is_edit": True})


# ==========================================
# --- DELETE VIEWS ---
# ==========================================

@login_required
def delete_theme(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    theme = get_object_or_404(Theme, pk=pk)
    theme.delete() 
    messages.success(request, "Theme and all related content deleted.")
    return redirect("learning:manage_content")

@login_required
def delete_section(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    section = get_object_or_404(Section, pk=pk)
    section.delete()
    messages.success(request, "Section deleted.")
    return redirect("learning:manage_content")

@login_required
def delete_word(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    word = get_object_or_404(Word, pk=pk)
    word.delete()
    messages.success(request, "Word deleted.")
    return redirect("learning:manage_content")


# --- ADD STORY ---
@login_required
def add_story(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")

    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Story successfully uploaded.")
            return redirect("learning:manage_content")
    else:
        form = StoryForm()
        
    return render(request, "learning/upload_story.html", {"form": form})

def story_library(request):
    stories = Story.objects.all().order_by('-story_id') 
    
    context = {
        'stories': stories
    }
    return render(request, 'learning/story_library.html', context)

# -> NEW MATH QUIZ VIEW <-
@login_required
def math_quiz(request):
    """
    Renders the math quiz page for kindergarteners.
    The actual math logic is handled client-side via JavaScript.
    """
    return render(request, "learning/math_quiz.html")

# ==========================================
# --- STORY QUIZ MANAGEMENT VIEWS ---
# ==========================================

@login_required
def add_question(request, story_id):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    story = get_object_or_404(Story, pk=story_id)

    if request.method == "POST":
        form = QuizQuestionForm(request.POST, request.FILES)
        formset = ChoiceFormSet(request.POST, request.FILES)
        
        if form.is_valid() and formset.is_valid():
            question = form.save(commit=False)
            question.story = story
            question.save()
            
            formset.instance = question
            formset.save()
            
            messages.success(request, "Question and choices added successfully.")
            return redirect("learning:manage_content") 
    else:
        form = QuizQuestionForm()
        formset = ChoiceFormSet()

    return render(request, "learning/manage_question.html", {
        "form": form, "formset": formset, "story": story, "is_edit": False
    })

@login_required
def edit_question(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    question = get_object_or_404(QuizQuestion, pk=pk)

    if request.method == "POST":
        form = QuizQuestionForm(request.POST, request.FILES, instance=question)
        formset = ChoiceFormSet(request.POST, request.FILES, instance=question)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Question updated successfully.")
            return redirect("learning:manage_content")
    else:
        form = QuizQuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    return render(request, "learning/manage_question.html", {
        "form": form, "formset": formset, "story": question.story, "is_edit": True
    })

@login_required
def delete_question(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    question = get_object_or_404(QuizQuestion, pk=pk)
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("learning:manage_content")


@login_required
def edit_story(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    story = get_object_or_404(Story, pk=pk)
    
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, "Story updated successfully.")
            return redirect("learning:manage_content")
    else:
        form = StoryForm(instance=story)
        
    return render(request, "learning/upload_story.html", {"form": form, "is_edit": True})

@login_required
def delete_story(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("index")
    story = get_object_or_404(Story, pk=pk)
    story.delete() 
    messages.success(request, "Story and all associated quizzes deleted.")
    return redirect("learning:manage_content")