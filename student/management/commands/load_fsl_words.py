import os
from django.core.management.base import BaseCommand
from django.core.files import File
from student.models import FSLWord  # <--- UPDATED: Imports the new model

# --- CONFIGURATION ---
# CHANGE THIS to the actual folder path on your computer where your videos are.
# Example for Windows: "C:/Users/KingJoe/Downloads/word_videos"
VIDEO_SOURCE_FOLDER = r"C:\Users\cillo\Downloads\THEME 1-20260217T083915Z-1-001\THEME 1"

class Command(BaseCommand):
    help = 'Loads FSL word videos from a local folder into the FSLWord table'

    def handle(self, *args, **kwargs):
        # 1. Sanity Check: Does the folder exist?
        if not os.path.exists(VIDEO_SOURCE_FOLDER):
            self.stdout.write(self.style.ERROR(f"Folder not found: {VIDEO_SOURCE_FOLDER}"))
            self.stdout.write(self.style.WARNING("Did you forget to change the VIDEO_SOURCE_FOLDER path in the script?"))
            return

        # 2. Get all video files
        files = [f for f in os.listdir(VIDEO_SOURCE_FOLDER) if f.lower().endswith(('.mp4', '.mov', '.avi'))]
        
        self.stdout.write(f"Found {len(files)} videos. Starting upload to FSLWord table...")

        count = 0
        for filename in files:
            # logic: "apple.mp4" -> word becomes "APPLE"
            word_text = os.path.splitext(filename)[0].upper()

            # 3. Check for duplicates in FSLWord table
            if FSLWord.objects.filter(word=word_text).exists():
                self.stdout.write(self.style.WARNING(f"Skipping {word_text} (Already exists)"))
                continue

            # 4. Save to Database
            try:
                file_path = os.path.join(VIDEO_SOURCE_FOLDER, filename)
                with open(file_path, 'rb') as f:
                    new_entry = FSLWord(word=word_text)
                    # The second argument to save() is the file content
                    new_entry.video.save(filename, File(f), save=True)
                
                self.stdout.write(self.style.SUCCESS(f"Uploaded: {word_text}"))
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to upload {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Done! Successfully uploaded {count} new words."))