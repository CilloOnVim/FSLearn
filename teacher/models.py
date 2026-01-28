from django.contrib.auth.models import User

# Create your models here.
from django.db import models


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher_profile"
    )

    # Teacher Information
    license_number = models.CharField(
        max_length=30, blank=True, help_text="LPT License No. (Optional)"
    )
    advisory_class = models.CharField(
        max_length=50, help_text="e.g. 'Kinder 1 - Apple Class'"
    )

    # To display a friendly picture to the kids
    profile_picture = models.ImageField(upload_to="teacher_pics/", blank=True)

    def __str__(self):
        return f"Teacher {self.user.last_name} ({self.advisory_class})"
