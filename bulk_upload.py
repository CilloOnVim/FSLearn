import os
import django
from django.core.files import File

# 1. POINT THIS TO YOUR ACTUAL PROJECT SETTINGS
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

# Import the model AFTER django.setup()
from student.models import FSLWord

def run_bulk_upload(videos_folder):
    """Loops through a folder (and its subfolders) of videos and adds them to the FSLWord database."""
    
    if not os.path.exists(videos_folder):
        print(f"❌ Error: The folder '{videos_folder}' does not exist. Skipping.")
        return 0

    added_count = 0

    for root, dirs, files in os.walk(videos_folder):
        for filename in files:
            if filename.lower().endswith(('.mp4', '.webm', '.mov')):
                
                word_text = os.path.splitext(filename)[0].upper()
                file_path = os.path.join(root, filename)

                if FSLWord.objects.filter(word__iexact=word_text).exists():
                    print(f"⚠️ Skipped: '{word_text}' already exists.")
                    continue

                try:
                    with open(file_path, 'rb') as video_file:
                        new_fsl_word = FSLWord(word=word_text)
                        new_fsl_word.video.save(filename, File(video_file), save=True)
                        added_count += 1
                        print(f"✅ Success: Uploaded '{word_text}' from {root}")
                except Exception as e:
                    print(f"❌ Failed to upload '{word_text}': {e}")

    return added_count

if __name__ == "__main__": 
    # Get the directory where THIS script is currently located
    BASE_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Assuming your THEME folders are in the exact same directory as this script.
    # If they are inside another folder (e.g., a 'videos' folder), change this to:
    # BASE_VIDEOS_DIR = os.path.join(BASE_SCRIPT_DIR, "videos")
    BASE_VIDEOS_DIR = BASE_SCRIPT_DIR

    # Define the themes you want to iterate through automatically
    THEMES_TO_PROCESS = ["THEME 1", "THEME 2", "THEME 3", "THEME 4"]
    
    grand_total = 0
    
    for theme in THEMES_TO_PROCESS:
        print(f"\n📂 Starting processing for: {theme}...")
        # Join the base directory with the theme name so it works on Windows or Linux
        theme_folder_path = os.path.join(BASE_VIDEOS_DIR, theme)
        
        theme_added_count = run_bulk_upload(theme_folder_path)
        grand_total += theme_added_count
        print(f"🏁 Finished {theme}. Added {theme_added_count} words.")

    print(f"\n🚀 ALL DONE! Grand total: Successfully added {grand_total} new words across all themes.")