import os
import django
from django.core.files import File

# 1. POINT THIS TO YOUR ACTUAL PROJECT SETTINGS
# Change 'myproject.settings' to whatever the folder name is that holds your settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

# Import the model AFTER django.setup()
from student.models import FSLWord

def run_bulk_upload(videos_folder):
    """Loops through a folder of videos and adds them to the FSLWord database."""
    
    if not os.path.exists(videos_folder):
        print(f"Error: The folder '{videos_folder}' does not exist.")
        return

    # Count successes for the final report
    added_count = 0

    for filename in os.listdir(videos_folder):
        # Only process video files
        if filename.lower().endswith(('.mp4', '.webm', '.mov')):
            # Strip the extension and uppercase it ("apple.mp4" -> "APPLE")
            word_text = os.path.splitext(filename)[0].upper()
            file_path = os.path.join(videos_folder, filename)

            # Prevent duplicate uploads from crashing the script
            if FSLWord.objects.filter(word__iexact=word_text).exists():
                print(f"⚠️ Skipped: '{word_text}' already exists in the database.")
                continue

            # Open the local file and save it to the Django model
            try:
                with open(file_path, 'rb') as video_file:
                    new_fsl_word = FSLWord(word=word_text)
                    # Django's .save() method automatically copies it to your media/fsl_words/ folder
                    new_fsl_word.video.save(filename, File(video_file), save=True)
                    added_count += 1
                    print(f"✅ Success: Uploaded '{word_text}'")
            except Exception as e:
                print(f"❌ Failed to upload '{word_text}': {e}")

    print(f"\n🚀 Done! Successfully added {added_count} new words to the dictionary.")

if __name__ == "__main__":
    # --- CHANGE THIS PATH TO WHERE YOUR VIDEOS ARE STORED ---
    # You can put a folder named 'raw_clips' next to manage.py and drop your videos there
    TARGET_FOLDER = "EDITED" 
    
    run_bulk_upload(TARGET_FOLDER)