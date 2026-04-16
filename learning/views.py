import json
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder

from .forms import SectionForm, ThemeForm, WordForm, StoryForm, QuizQuestionForm, ChoiceFormSet
from .models import Section, Theme, Word, SentenceQuiz, QuizQuestion, Story, VocabQuiz
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


# THE HUB (was moved to teacher app)


# 1. ADD WORD
@login_required
def upload_word(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")

    if request.method == "POST":
        form = WordForm(request.POST, request.FILES)
        if form.is_valid():
            word_obj = form.save()
            
            # --- NEW: Add to FSLWord for NLP sentence restructuring ---
            import re
            match = re.search(r'\((.*?)\)', word_obj.name)
            fsl_target_word = match.group(1).strip() if match else word_obj.name.strip()
            
            # Map it so the drag & drop can find the same video clip
            FSLWord.objects.get_or_create(
                word__iexact=fsl_target_word,
                defaults={
                    'word': fsl_target_word.upper(),
                    'video': word_obj.video
                }
            )
            # ----------------------------------------------------------

            return redirect("teacher:teacher_dashboard")
    else:
        form = WordForm()

    return render(request, "learning/upload_word.html", {"form": form})


# 2. ADD THEME
@login_required
def add_theme(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")

    if request.method == "POST":
        form = ThemeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("teacher:manage_content")
    else:
        form = ThemeForm()
    return render(request, "learning/upload_theme.html", {"form": form})


# 3. ADD SECTION
@login_required
def add_section(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")

    if request.method == "POST":
        form = SectionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("teacher:manage_content")
    else:
        form = SectionForm()
    return render(request, "learning/upload_section.html", {"form": form})


# 5. STORY LIST (Pick a story)
@login_required
def quiz_select(request):
    return render(request, "learning/story_list.html")


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
        return redirect("core:index")
    
    quizzes = SentenceQuiz.objects.all().order_by('-created_at')
    return render(request, "learning/manage_quizzes.html", {"quizzes": quizzes})

# 8. CREATE QUIZ (The Magic Builder)
@login_required
def create_quiz(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")

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
        ).values_list('quiz_id', flat=True).distinct()

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
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    theme = get_object_or_404(Theme, pk=pk)
    
    if request.method == "POST":
        form = ThemeForm(request.POST, request.FILES, instance=theme)
        if form.is_valid():
            form.save()
            messages.success(request, "Theme updated successfully.")
            return redirect("teacher:manage_content")
    else:
        form = ThemeForm(instance=theme)
        
    return render(request, "learning/upload_theme.html", {"form": form, "is_edit": True})

@login_required
def edit_section(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    section = get_object_or_404(Section, pk=pk)
    
    if request.method == "POST":
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, "Section updated.")
            return redirect("teacher:manage_content")
    else:
        form = SectionForm(instance=section)
    return render(request, "learning/upload_section.html", {"form": form, "is_edit": True})

@login_required
def edit_word(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    word = get_object_or_404(Word, pk=pk)
    
    if request.method == "POST":
        form = WordForm(request.POST, request.FILES, instance=word)
        if form.is_valid():
            word_obj = form.save()
            
            # --- NEW: Sync with FSLWord for NLP sentence restructuring ---
            import re
            match = re.search(r'\((.*?)\)', word_obj.name)
            fsl_target_word = match.group(1).strip() if match else word_obj.name.strip()
            
            # Attempt to find the existing word and update its video, or create
            fsl_word, created = FSLWord.objects.get_or_create(
                word__iexact=fsl_target_word,
                defaults={
                    'word': fsl_target_word.upper(),
                    'video': word_obj.video
                }
            )
            if not created and word_obj.video:
                fsl_word.video = word_obj.video
                fsl_word.save()
            # -------------------------------------------------------------

            messages.success(request, "Word updated.")
            return redirect("teacher:manage_content")
    else:
        form = WordForm(instance=word)
    return render(request, "learning/upload_word.html", {"form": form, "is_edit": True})


# ==========================================
# --- DELETE VIEWS ---
# ==========================================

@login_required
def delete_theme(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    theme = get_object_or_404(Theme, pk=pk)
    theme.delete() 
    messages.success(request, "Theme and all related content deleted.")
    return redirect("teacher:manage_content")

@login_required
def delete_section(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    section = get_object_or_404(Section, pk=pk)
    section.delete()
    messages.success(request, "Section deleted.")
    return redirect("teacher:manage_content")

@login_required
def delete_word(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    word = get_object_or_404(Word, pk=pk)
    word.delete()
    messages.success(request, "Word deleted.")
    return redirect("teacher:manage_content")


# --- ADD STORY ---
@login_required
def add_story(request):
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")

    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Story successfully uploaded.")
            return redirect("teacher:manage_content")
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
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
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
            return redirect("teacher:manage_content") 
    else:
        form = QuizQuestionForm()
        formset = ChoiceFormSet()

    return render(request, "learning/manage_question.html", {
        "form": form, "formset": formset, "story": story, "is_edit": False
    })

@login_required
def edit_question(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    question = get_object_or_404(QuizQuestion, pk=pk)

    if request.method == "POST":
        form = QuizQuestionForm(request.POST, request.FILES, instance=question)
        formset = ChoiceFormSet(request.POST, request.FILES, instance=question)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Question updated successfully.")
            return redirect("teacher:manage_content")
    else:
        form = QuizQuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    return render(request, "learning/manage_question.html", {
        "form": form, "formset": formset, "story": question.story, "is_edit": True
    })

@login_required
def delete_question(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    question = get_object_or_404(QuizQuestion, pk=pk)
    question.delete()
    messages.success(request, "Question deleted.")
    return redirect("teacher:manage_content")


@login_required
def edit_story(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    story = get_object_or_404(Story, pk=pk)
    
    if request.method == "POST":
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, "Story updated successfully.")
            return redirect("teacher:manage_content")
    else:
        form = StoryForm(instance=story)
        
    return render(request, "learning/upload_story.html", {"form": form, "is_edit": True})

@login_required
def delete_story(request, pk):
    if not hasattr(request.user, "teacher_profile"): return redirect("core:index")
    story = get_object_or_404(Story, pk=pk)
    story.delete() 
    messages.success(request, "Story and all associated quizzes deleted.")
    return redirect("teacher:manage_content")


# ==========================================
# --- VOCAB QUIZ MANAGEMENT VIEWS ---
# ==========================================
@login_required
def manage_vocab_quizzes(request):
    """Teacher dashboard to manage all vocab quizzes via toggle switches."""
    if not hasattr(request.user, "teacher_profile"):
        return redirect("core:index")
        
    themes = Theme.objects.prefetch_related('sections__vocab_quizzes').all().order_by('order')
    return render(request, "learning/manage_vocab_quizzes.html", {"themes": themes})

@login_required
def toggle_vocab_quiz(request, section_id):
    """API endpoint to toggle a vocab quiz's active state."""
    if not hasattr(request.user, "teacher_profile") or request.method != "POST":
        return JsonResponse({"error": "Unauthorized or invalid method"}, status=400)
    
    section = get_object_or_404(Section, pk=section_id)
    quiz, created = VocabQuiz.objects.get_or_create(section=section)
    
    if not created:
        quiz.is_active = not quiz.is_active
        quiz.save()
        
    return JsonResponse({
        "success": True,
        "is_active": quiz.is_active,
        "section_title": section.title
    })

@login_required
def take_vocab_quiz(request, quiz_id):
    quiz = get_object_or_404(VocabQuiz, pk=quiz_id)
    
    # 1. Grab 5 random words from this section
    # Use order_by('?') for random sorting
    target_words = list(quiz.section.words.exclude(video="").order_by('?')[:5])
    
    quiz_data = []
    for target in target_words:
        # 2. Grab 3 random distractors from other sections
        distractors = list(Word.objects.exclude(section=quiz.section).exclude(video="").order_by('?')[:3])
        
        # Fallback if DB doesn't have words in other sections
        if len(distractors) < 3:
            distractors = list(Word.objects.exclude(pk=target.pk).exclude(video="").order_by('?')[:3])
            
        # 3. Compile and shuffle
        choices = [
            {"video_url": target.video.url if target.video else "", "is_correct": True}
        ]
        for d in distractors:
            choices.append({"video_url": d.video.url if d.video else "", "is_correct": False})
            
        random.shuffle(choices)
        
        quiz_data.append({
            "target_word": target.name,
            "target_image": target.image.url if target.image else "",
            "choices": choices
        })
        
    context = {
        "quiz": quiz,
        "quiz_data_json": json.dumps(quiz_data)
    }
    return render(request, "learning/take_vocab_quiz.html", context)

@login_required
def vocab_quiz_list(request):
    quizzes = VocabQuiz.objects.filter(is_active=True).order_by('-vocabquiz_id')
    passed_quiz_ids = []
    if hasattr(request.user, 'student_profile'):
        passed_quiz_ids = request.user.student_profile.vocab_quiz_scores.filter(
            passed=True
        ).values_list('vocab_quiz_id', flat=True).distinct()
        
    return render(request, "learning/vocab_quiz_list.html", {
        "quizzes": quizzes,
        "passed_quiz_ids": passed_quiz_ids
    })

