import os
import django
from django.core.files import File

# 1. POINT THIS TO YOUR ACTUAL PROJECT SETTINGS
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

# Import the model AFTER django.setup()
from student.models import FSLWord

def run_bulk_upload():
    print("🚀 Initializing Render Bulk Upload Sequence...")
    
    # Get the current working directory (Render runs from the project root)
    base_dir = os.getcwd()
    videos_folder = os.path.join(base_dir, "renamed_ready")

    if not os.path.exists(videos_folder):
        print(f"❌ FATAL ERROR: The folder '{videos_folder}' was not found.")
        print("Did you remember to push the 'renamed_ready' folder to GitHub?")
        return 0

    print(f"📂 Found target directory: {videos_folder}")
    added_count = 0
    skipped_count = 0
    failed_count = 0

    for root, dirs, files in os.walk(videos_folder):
        for filename in files:
            if filename.lower().endswith(('.mp4', '.webm', '.mov')):
                
                # Strip the extension to get the word
                word_text = os.path.splitext(filename)[0].upper()
                file_path = os.path.join(root, filename)

                # Check if it already exists to prevent duplicates if the script fails halfway
                if FSLWord.objects.filter(word__iexact=word_text).exists():
                    print(f"⚠️ Skipped: '{word_text}' already exists in database.")
                    skipped_count += 1
                    continue

                try:
                    # Upload to database (and Cloudinary)
                    with open(file_path, 'rb') as video_file:
                        new_fsl_word = FSLWord(word=word_text)
                        new_fsl_word.video.save(filename, File(video_file), save=True)
                        added_count += 1
                        print(f"✅ Success [{added_count}]: Uploaded '{word_text}' to database/cloud.")
                except Exception as e:
                    print(f"❌ Failed to upload '{word_text}': {e}")
                    failed_count += 1

    print("\n" + "="*40)
    print("🏁 BULK UPLOAD COMPLETE")
    print(f"✅ Successfully Added: {added_count}")
    print(f"⚠️ Skipped (Duplicates): {skipped_count}")
    print(f"❌ Failed: {failed_count}")
    print("="*40 + "\n")

if __name__ == "__main__": 
    run_bulk_upload()