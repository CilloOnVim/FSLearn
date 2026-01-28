# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Database model ito Mam para ma-store lahat nung alphabet letters.
# Ganito kasi Mam mag declare ng database sa django compared sa kung PHP gamitin


class FSLSign(models.Model):
    # Ginamitan ng CharField with max_length=5 imbis na 1 para ma-accomodate din yung Ng
    char = models.CharField(
        max_length=5, unique=True, help_text="The letter or number (e.g., 'A', '1')"
    )
    # FileField para makapag upload nung MP4 files
    media_file = models.FileField(
        upload_to="fsl_clips/", help_text="Upload the hand sign clip here"
    )

    def __str__(self):
        return f"Sign for {self.char}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student_profile"
    )

    # --- KINDERGARTEN SPECIFIC FIELDS ---
    nickname = models.CharField(
        max_length=50, help_text="What the kid wants to be called (e.g. 'King Joe')"
    )

    level = models.CharField(
        max_length=20,
        choices=[
            ("Nursery", "Nursery"),
            ("Kinder 1", "Kinder 1"),
            ("Kinder 2", "Kinder 2"),
            ("Prep", "Preparatory"),
        ],
        default="Kinder 1",
    )

    section = models.CharField(
        max_length=20, help_text="e.g. 'Blueberry Class' or 'Morning Session'"
    )

    # Guardian Info is mandatory for Kinder apps
    guardian_name = models.CharField(max_length=100, help_text="Parent/Guardian Name")

    # Visual Identification (Kids can't read well, they need images)
    avatar = models.ImageField(
        upload_to="student_avatars/", default="default_avatar.png"
    )

    def __str__(self):
        return f"{self.nickname} ({self.level})"


# --- SIGNAL AUTOMATION ---
# Keeps the profile synced when a User is created
@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    if created and not instance.is_staff:
        # We create the profile, but the teacher/admin will likely fill in the details later
        StudentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    if not instance.is_staff:
        instance.student_profile.save()
