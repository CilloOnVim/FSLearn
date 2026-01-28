import os

from django.conf import settings
from django.core.management.base import BaseCommand

from student.models import FSLSign


class Command(BaseCommand):
    help = "Loads FSL alphabet clips from the media folder into the database"

    def handle(self, *args, **kwargs):
        clips_dir = os.path.join(settings.MEDIA_ROOT, "fsl_clips")

        if not os.path.exists(clips_dir):
            self.stdout.write(self.style.ERROR(f"Directory not found: {clips_dir}"))
            return

        count = 0
        for filename in os.listdir(clips_dir):
            if filename.endswith(".mp4"):
                # "Ng.mp4" -> "ng"
                char = filename.split(".")[0].lower()

                # --- THE FIX IS HERE ---
                # Allow if length is 1 (a, b, ñ) OR if it is specifically 'ng'
                if len(char) == 1 or char == "ng":
                    relative_path = f"fsl_clips/{filename}"

                    sign, created = FSLSign.objects.get_or_create(
                        char=char, defaults={"media_file": relative_path}
                    )

                    if not created:
                        sign.media_file = relative_path
                        sign.save()
                        self.stdout.write(f"Updated sign for: {char}")
                    else:
                        self.stdout.write(
                            self.style.SUCCESS(f"Created sign for: {char}")
                        )

                    count += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Skipped file (name too long): {filename}")
                    )

        self.stdout.write(self.style.SUCCESS(f"Successfully processed {count} clips."))
