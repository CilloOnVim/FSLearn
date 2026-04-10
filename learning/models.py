import os
from django.core.files.storage import FileSystemStorage
from cloudinary_storage.storage import VideoMediaCloudinaryStorage
from django.db import models
from django.utils.text import slugify

# This function dynamically checks your .env file
def get_video_storage():
    if os.environ.get('ENVIRONMENT') == 'production':
        return VideoMediaCloudinaryStorage()
    return FileSystemStorage()

# --- 1. THEME MODEL ---
class Theme(models.Model):
    theme_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200, help_text="e.g., 'Theme 1: Knowing Who We Are'")
    description = models.TextField(blank=True, help_text="Short description of this theme.")
    icon = models.ImageField(upload_to="themes/icons/", blank=True, null=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title

# --- 2. SECTION MODEL ---
class Section(models.Model):
    section_id = models.BigAutoField(primary_key=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=200, help_text="e.g., 'Basic Identity', 'Emotions'")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.theme.title} - {self.title}"

# --- 3. WORD MODEL ---
class Word(models.Model):
    word_id = models.BigAutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="words")
    name = models.CharField(max_length=100, help_text="e.g., 'MASAYA (Happy)'")
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from Name (e.g., 'masaya-happy')")
    video = models.FileField(
        upload_to="words/videos/", 
        storage=get_video_storage, # <-- FIXED
        help_text="Upload the MP4 sign language clip here"
    )
    image = models.ImageField(upload_to="words/images/", help_text="Upload the illustration/drawing here")
    description = models.TextField(help_text="Instructions: e.g., 'Smile with both hands moving up...'")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            new_slug = base_slug
            counter = 1
            # Keep incrementing the counter until we find a slug that isn't taken
            while Word.objects.filter(slug=new_slug).exists():
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = new_slug
        super().save(*args, **kwargs)


# --- 4. STORY MODEL ---
class Story(models.Model):
    story_id = models.BigAutoField(primary_key=True)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=200)
    video = models.FileField(
        upload_to="stories/videos/", 
        storage=get_video_storage, # <-- FIXED
        help_text="The main story video"
    )
    thumbnail = models.ImageField(upload_to="stories/thumbnails/", blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

# --- 5. QUIZ QUESTION ---
class QuizQuestion(models.Model):
    question_id = models.BigAutoField(primary_key=True)
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name="questions")
    video = models.FileField(
        upload_to="stories/quiz_videos/", 
        storage=get_video_storage, # <-- FIXED
        help_text="Video of the teacher asking the question"
    )
    text = models.CharField(max_length=255, help_text="Text version of the question (optional)")
    
    def __str__(self):
        return f"Q: {self.text} ({self.story.title})"

# --- 6. QUIZ CHOICE ---
class QuizChoice(models.Model):
    choice_id = models.BigAutoField(primary_key=True)
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200, help_text="The answer text displayed on the tile")
    image = models.ImageField(upload_to="stories/choices/", blank=True, null=True, help_text="Optional image for the choice")
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} - {'Correct' if self.is_correct else 'Wrong'}"

# --- 7. SENTENCE QUIZ ---
class SentenceQuiz(models.Model):
    sentencequiz_id = models.BigAutoField(primary_key=True)
    original_text = models.CharField(max_length=255)
    structure_json = models.JSONField(help_text="Stores the Time, Topic, Comment breakdown")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_text

# --- 8. VOCAB QUIZ ---
class VocabQuiz(models.Model):
    vocabquiz_id = models.BigAutoField(primary_key=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="vocab_quizzes")
    passing_score = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Vocab Quiz for: {self.section.title}"