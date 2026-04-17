import os
from datetime import timedelta
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# This function dynamically checks your .env file
def get_video_storage():
    if os.environ.get('ENVIRONMENT') == 'production':
        return VideoMediaCloudinaryStorage()
    return FileSystemStorage()

class FSLSign(models.Model):
    fslsign_id = models.BigAutoField(primary_key=True)
    char = models.CharField(max_length=5, unique=True, help_text="The letter or number (e.g., 'A', '1')")
    media_file = models.FileField(
        upload_to="fsl_clips/", 
        storage=get_video_storage, # <-- FIXED
        help_text="Upload the hand sign clip here"
    )

    def __str__(self):
        return f"Sign for {self.char}"

class FSLWord(models.Model):
    fslword_id = models.BigAutoField(primary_key=True)
    word = models.CharField(max_length=100, unique=True, help_text="e.g. 'EAT', 'APPLE'")
    video = models.FileField(
        upload_to="fsl_words/", 
        storage=get_video_storage, # <-- FIXED
        help_text="Upload word video here"
    )

    def __str__(self):
        return f"Word: {self.word.upper()}"

class StudentProfile(models.Model):
    studentprofile_id = models.BigAutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student_profile")
    nickname = models.CharField(max_length=50, help_text="What the kid wants to be called (e.g. 'King Joe')")
    level = models.CharField(
        max_length=20,
        choices=[("Nursery", "Nursery"), ("Kinder 1", "Kinder 1"), ("Kinder 2", "Kinder 2"), ("Prep", "Preparatory")],
        default="Kinder 1",
    )
    section = models.CharField(max_length=20, help_text="e.g. 'Blueberry Class' or 'Morning Session'")
    guardian_name = models.CharField(max_length=100, help_text="Parent/Guardian Name")
    avatar = models.ImageField(upload_to="student_avatars/", default="default_avatar.png")
    last_active = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.nickname} ({self.level})"

    @property
    def is_online(self):
        if self.last_active:
            # Consider online if active within the last 5 minutes
            return timezone.now() - self.last_active < timedelta(minutes=5)
        return False
    
class WordProgress(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="completed_words")
    word = models.ForeignKey("learning.Word", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A student can only complete a specific word once
        unique_together = ("student", "word")

class QuizProgress(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="quiz_scores")
    quiz = models.ForeignKey("learning.SentenceQuiz", on_delete=models.CASCADE)
    is_passed = models.BooleanField(default=False)
    details = models.JSONField(blank=True, null=True, help_text="Stored incorrect sequences")
    completed_at = models.DateTimeField(auto_now_add=True)

class StoryQuizProgress(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="story_quiz_scores")
    story = models.ForeignKey("learning.Story", on_delete=models.CASCADE)
    score = models.IntegerField(default=0, help_text="Number of questions answered correctly")
    is_passed = models.BooleanField(default=False)
    details = models.JSONField(blank=True, null=True, help_text="Questions answered incorrectly")
    completed_at = models.DateTimeField(auto_now_add=True)

class VocabQuizProgress(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="vocab_quiz_scores")
    vocab_quiz = models.ForeignKey("learning.VocabQuiz", on_delete=models.CASCADE)
    score = models.IntegerField()
    passed = models.BooleanField()
    details = models.JSONField(blank=True, null=True, help_text="Words answered incorrectly")
    completed_at = models.DateTimeField(auto_now_add=True)
