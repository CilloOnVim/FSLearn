from django.db import models
from django.utils.text import slugify

# Create your models here.

# --- 1. THEME MODEL (e.g., "Knowing Who We Are") ---
class Theme(models.Model):
    title = models.CharField(max_length=200, help_text="e.g., 'Theme 1: Knowing Who We Are'")
    description = models.TextField(blank=True, help_text="Short description of this theme.")

    # Optional: Icon for the main menu card
    icon = models.ImageField(upload_to='themes/icons/', blank=True, null=True)

    # Ordering: Controls which theme appears first (1, 2, 3...)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# --- 2. SECTION MODEL (e.g., "Emotions", "Family Members") ---
class Section(models.Model):
    # Links this section to a specific Theme
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name='sections')

    title = models.CharField(max_length=200, help_text="e.g., 'Basic Identity', 'Emotions'")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.theme.title} - {self.title}"


# --- 3. WORD MODEL (e.g., "MASAYA", "NANAY") ---
class Word(models.Model):
    # Links this word to a specific Section
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='words')

    name = models.CharField(max_length=100, help_text="e.g., 'MASAYA (Happy)'")

    # The Slug is CRITICAL for your URL routing.
    # unique=True ensures we don't have two pages with the exact same link.
    slug = models.SlugField(unique=True, blank=True, help_text="Auto-generated from Name (e.g., 'masaya-happy')")

    # Media Files
    video = models.FileField(upload_to='words/videos/', help_text="Upload the MP4 sign language clip here")
    image = models.ImageField(upload_to='words/images/', help_text="Upload the illustration/drawing here")

    description = models.TextField(help_text="Instructions: e.g., 'Smile with both hands moving up...'")

    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

    # AUTOMATIC SLUG GENERATOR
    # This function runs every time you hit 'Save'.
    # If you didn't type a slug, it creates one from the Name.
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
