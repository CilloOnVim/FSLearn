from re import A

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from .forms import SectionForm, ThemeForm, WordForm, StoryForm, QuizQuestionForm, ChoiceFormSet
from .models import Section, Theme, Word, SentenceQuiz, QuizQuestion
import json
from django.core.serializers.json import DjangoJSONEncoder
from student.nlp_utils import translate_to_fsl
import random

# ... existing imports ...
from student.nlp_utils import translate_to_fsl 
from .models import SentenceQuiz
from .models import Story  # Import the new models
from student.models import FSLWord

# Create your views here.


# 1. THEME LIST
def theme_list(request):
    themes = Theme.objects.all()
    return render(request, "learning/theme_list.html", {"themes": themes})


# 2. SECTION LIST
def section_list(request, theme_id):
    theme = get_object_or_404(Theme, pk=theme_id)
    sections = theme.sections.all()  # Uses the 'related_name' from models.py
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
# views.py

@login_required
def manage_content(request):
    # Check if teacher
    if not hasattr(request.user, "teacher_profile"):
        return redirect("index")
    
    # FETCH DATA: Get all themes, and pre-load their sections and words.
    # 'sections__words' joins the 3 tables efficiently in one go.
    themes = Theme.objects.prefetch_related('sections__words').all()
    
    return render(request, "learning/manage_content.html", {
        "themes": themes
    })


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

# 5. STORY LIST (Pick a story)
@login_required
def story_list(request):
    stories = Story.objects.all()
    # POINTS TO THE NEW MENU FILE
    return render(request, "learning/story_list.html", {"stories": stories})

# 6. STORY PLAYER & QUIZ (The logic)
def story_view(request, story_id):
    story = get_object_or_404(Story, id=story_id)
    
    questions_data = []
    questions = story.questions.all()
    
    for q in questions:
        # CRITICAL FIX: Skip questions if they have no video, otherwise the page crashes
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
            "video_url": q.video.url, # This now matches what your JS expects
            "text": q.text,
            "choices": choices
        })

    context = {
        "story": story,
        "quiz_data_json": json.dumps(questions_data, cls=DjangoJSONEncoder)
    }
    # POINTS TO THE RENAMED PLAYER FILE
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
        action = request.POST.get("action") # 'analyze' or 'save'

        if sentence:
            # 1. Run the NLP (Time-Topic-Comment)
            # This returns dict like: {'time': 'TODAY', 'topic': 'APPLE', 'comment': 'EAT', 'complete': '...'}
            nlp_result = translate_to_fsl(sentence) 
            
            # 2. Check Database for Videos
            # We want to tell the teacher which words are missing videos!
            analysis_report = []
            
            # Combine all words into one list to check them
            words_to_check = []
            if nlp_result.get('time'): words_to_check.append((nlp_result['time'], 'Time'))
            if nlp_result.get('topic'): words_to_check.append((nlp_result['topic'], 'Topic'))
            if nlp_result.get('comment'): words_to_check.append((nlp_result['comment'], 'Action'))

            all_good = True

            for word_text, category in words_to_check:
                # Check FSLWord table (case insensitive)
                # We assume your model is FSLWord (student app) or Word (learning app). 
                # Based on previous chat, you had FSLWord in student/models.py. 
                # If it's in 'learning', change FSLWord to Word.
                from student.models import FSLWord 
                
                exists = FSLWord.objects.filter(word__iexact=word_text).exists()
                
                analysis_report.append({
                    "word": word_text,
                    "category": category,
                    "has_video": exists
                })
                if not exists:
                    all_good = False

            context = {
                "original": sentence,
                "nlp_result": nlp_result,
                "report": analysis_report,
                "all_good": all_good
            }

            # 3. Save if requested
            if action == "save":
                SentenceQuiz.objects.create(
                    original_text=sentence,
                    structure_json=nlp_result
                )
                messages.success(request, "Quiz saved successfully!")
                return redirect("learning:manage_quizzes")

    return render(request, "learning/create_quiz.html", context)

# 9. DELETE QUIZ
@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(SentenceQuiz, id=quiz_id)
    quiz.delete()
    messages.success(request, "Quiz deleted.")
    return redirect("learning:manage_quizzes")


@login_required
def sentence_quiz_list(request):
    """Shows all available puzzles to the student"""
    quizzes = SentenceQuiz.objects.all().order_by('-created_at')
    return render(request, "learning/quiz_list.html", {"quizzes": quizzes})

@login_required
def take_sentence_quiz(request, quiz_id):
    """The actual drag-and-drop player"""
    quiz = get_object_or_404(SentenceQuiz, pk=quiz_id)

    # 1. Get the correct FSL sequence (e.g., "YESTERDAY APPLE ME EAT")
    correct_sequence_str = quiz.structure_json.get('complete', '')
    correct_words = correct_sequence_str.split()

    # 2. Build the tile data and fetch videos
    tiles = []
    for index, word in enumerate(correct_words):
        fsl_word = FSLWord.objects.filter(word__iexact=word).first()
        video_url = fsl_word.video.url if fsl_word and fsl_word.video else None

        tiles.append({
            "id": f"tile_{index}", # Unique ID for the frontend
            "word": word,
            "video_url": video_url
        })

    # 3. Shuffle the tiles so the student has to solve it
    shuffled_tiles = list(tiles)
    random.shuffle(shuffled_tiles)

    context = {
        "quiz": quiz,
        "shuffled_tiles": shuffled_tiles,
        # Pass the correct sequence to JavaScript for validation
        "correct_sequence_json": json.dumps(correct_words) 
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
        # 'instance=theme' is the magic keyword that updates instead of creates
        form = ThemeForm(request.POST, request.FILES, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, "Theme updated successfully.")
            return redirect("learning:manage_content")
    else:
        form = ThemeForm(instance=theme)
        
    # We recycle your existing upload template!
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
    theme.delete() # Because of CASCADE in models, this deletes its sections and words too!
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
        # request.FILES is absolutely mandatory here. If you forget it, the video will not upload!
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Story successfully uploaded.")
            return redirect("learning:manage_content")
    else:
        form = StoryForm()
        
    return render(request, "learning/upload_story.html", {"form": form})


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
            # Save the question first, but don't commit yet so we can attach the story
            question = form.save(commit=False)
            question.story = story
            question.save()
            
            # Now save the choices and link them to the question we just saved
            formset.instance = question
            formset.save()
            
            messages.success(request, "Question and choices added successfully.")
            return redirect("learning:manage_content") # Or redirect to a story detail management page
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
    # This automatically deletes the QuizChoices too because of CASCADE
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
    story.delete() # This nukes the story AND all attached questions/choices
    messages.success(request, "Story and all associated quizzes deleted.")
    return redirect("learning:manage_content")



