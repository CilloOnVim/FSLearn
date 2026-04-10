# student/views.py

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from learning.models import Word, SentenceQuiz, VocabQuiz
from .models import WordProgress, QuizProgress, StoryQuizProgress, VocabQuizProgress

# CRITICAL: Import both models
from .models import FSLSign, FSLWord 
from .nlp_utils import translate_to_fsl


# --- 1. FINGERSPELLING (Uses FSLSign / Alphabet) ---
def translator_view(request):
    # Fetch all signs (A-Z, 0-9)
    signs = FSLSign.objects.all()

    # Map char -> media_file (e.g., 'a': '/media/fsl_alphabet/a.mp4')
    sign_map = {sign.char.lower(): sign.media_file.url for sign in signs}

    context = {
        "sign_map": json.dumps(sign_map)
    }
    return render(request, "student/fsl_translator.html", context)

# --- 2. SENTENCE RESTRUCTURING (Uses FSLWord / Vocabulary) ---
@login_required
def restructure_sentence_view(request):
    context = {}
    if request.method == "POST":
        original_text = request.POST.get("sentence", "")
        if original_text:
            nlp_results = translate_to_fsl(original_text)
            gloss_words = nlp_results['complete'].split()
            
            visual_sequence = []
            
            for word_text in gloss_words:
                
                # 1. Check for Explicit Tag (from NLP like fs-SPACE)
                if word_text.startswith("fs-"):
                    clean_name = word_text.replace("fs-", "")
                    sign_obj = FSLSign.objects.filter(char__iexact=clean_name).first()
                    
                    if sign_obj and sign_obj.media_file:
                        visual_sequence.append({
                            "word": clean_name, 
                            "video_url": sign_obj.media_file.url,
                            "type": "letter"
                        })
                    else:
                        visual_sequence.append({
                            "word": f"[{clean_name}]",
                            "video_url": None,
                            "type": "text"
                        })

                # 2. Check for Name Tags (e.g., name-ANDRES_BONIFACIO)
                elif word_text.startswith("name-"):
                    # Strip the tag and put the space back
                    clean_name = word_text.replace("name-", "").replace("_", " ")
                    
                    # Look for the full name in the vocabulary database first
                    word_obj = FSLWord.objects.filter(word__iexact=clean_name).first()
                    
                    if word_obj and word_obj.video:
                        # You have a custom sign for this person! Use it.
                        visual_sequence.append({
                            "word": clean_name,
                            "video_url": word_obj.video.url,
                            "type": "video"
                        })
                    else:
                        # You don't have a video for them. Fallback to fingerspelling the whole string.
                        visual_sequence.extend(get_fingerspell_sequence(clean_name))

                # 3. Check standard Word Database
                else:
                    word_obj = FSLWord.objects.filter(word__iexact=word_text).first()
                    
                    if word_obj and word_obj.video:
                        visual_sequence.append({
                            "word": word_text,
                            "video_url": word_obj.video.url,
                            "type": "video"
                        })
                    else:
                        # Unknown vocabulary word fallback
                        visual_sequence.extend(get_fingerspell_sequence(word_text))

            context = {
                "original": original_text,
                "results": nlp_results,
                "visual_sequence": visual_sequence
            }
    
    return render(request, "student/fsl_restructure.html", context)

# --- HELPER FUNCTION ---
def get_fingerspell_sequence(text):
    """
    Breaks a text into individual letters/digraphs (handles Filipino 'NG' and Spaces) 
    and finds their videos. Returns a list of dictionaries.
    """
    sequence = []
    i = 0
    text_length = len(text)
    
    # Store the original word for the UI display
    original_word = text.upper()

    while i < text_length:
        # 1. Peek ahead to catch the "NG" digraph
        if i + 1 < text_length and text[i:i+2].upper() == "NG":
            char = "NG"
            i += 2  # Skip the 'G' in the next iteration
        else:
            char = text[i].upper()
            i += 1
            
        # --- THE FIX: Intercept spaces before the alpha check ---
        if char == " ":
            char = "SPACE"
        elif not char.isalpha() and char not in ["Ñ", "NG"]:
            continue
            
        # 2. Database Lookup
        letter_obj = FSLSign.objects.filter(char__iexact=char).first()
        
        if letter_obj and letter_obj.media_file:
            sequence.append({
                "word": f"{original_word} ({char})", # Displays "RON ANTHONY (SPACE)"
                "video_url": letter_obj.media_file.url,
                "type": "letter"
            })
        else:
            # Absolute worst case: No video for the letter
            sequence.append({
                "word": f"{original_word} ({char})",
                "video_url": None,
                "type": "text"
            })
            
    return sequence

# --- 3. DASHBOARD ---
@login_required
def student_dashboard(request):
    try:
        student = request.user.student_profile
    except AttributeError:
        return redirect('index')

    # Calculate basic progress stats
    words_learned = student.completed_words.count()
    quizzes_passed = student.quiz_scores.filter(is_passed=True).count()
    story_quizzes_passed = student.story_quiz_scores.filter(is_passed=True).count()

    context = {
        'student': student,
        'words_learned': words_learned,
        'quizzes_passed': quizzes_passed,
        'story_quizzes_passed': story_quizzes_passed,
    }
    return render(request, 'student/student_dashboard.html', context)


@login_required
def mark_word_done(request, word_id):
    if request.method == "POST" and hasattr(request.user, "student_profile"):
        word = get_object_or_404(Word, pk=word_id)
        # get_or_create prevents duplicate spam if they refresh the page
        WordProgress.objects.get_or_create(student=request.user.student_profile, word=word)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def save_quiz_score(request, quiz_id):
    if request.method == "POST" and hasattr(request.user, "student_profile"):
        quiz = get_object_or_404(SentenceQuiz, pk=quiz_id)
        # Expecting the frontend to send a 'passed' boolean
        passed = request.POST.get("passed") == "true"
        
        progress, created = QuizProgress.objects.get_or_create(
            student=request.user.student_profile, 
            quiz=quiz,
            defaults={'is_passed': passed}
        )
        
        # If it already existed but wasn't passed, update it if they just passed
        if not created and passed and not progress.is_passed:
            progress.is_passed = True
            progress.save()
            
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def save_story_quiz_score(request, story_id):
    if request.method == "POST" and hasattr(request.user, "student_profile"):
        from learning.models import Story
        story = get_object_or_404(Story, pk=story_id)
        
        # Expecting the frontend to send a 'score' and 'passed'
        score = int(request.POST.get("score", 0))
        passed = request.POST.get("passed") == "true"
        
        # Update or create the progress record
        progress, created = StoryQuizProgress.objects.get_or_create(
            student=request.user.student_profile, 
            story=story,
            defaults={'score': score, 'is_passed': passed}
        )
        
        # If it already existed, update with the best score
        if not created:
            if score > progress.score:
                progress.score = score
            if passed:
                progress.is_passed = True
            progress.save()
            
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def save_vocab_quiz_score(request, quiz_id):
    if request.method == "POST" and hasattr(request.user, "student_profile"):
        quiz = get_object_or_404(VocabQuiz, pk=quiz_id)
        
        score = int(request.POST.get("score", 0))
        passed = request.POST.get("passed") == "true"
        
        progress, created = VocabQuizProgress.objects.get_or_create(
            student=request.user.student_profile,
            vocab_quiz=quiz,
            defaults={'score': score, 'passed': passed}
        )
        
        if not created:
            if score > progress.score:
                progress.score = score
            if passed:
                progress.passed = True
            progress.save()
            
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)