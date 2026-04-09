print("HEY, THE SCRIPT IS EXECUTING!")

import os
import django
from django.core.files import File

# Do not screw this up again. Leave it as FSLearn.settings.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from student.models import FSLSign

def run_alphabet_upload(videos_folder):
    """Loops through a folder of alphabet videos and adds them to the FSLSign database."""
    
    if not os.path.exists(videos_folder):
        print(f"Error: The folder '{videos_folder}' does not exist. Make it and drop the videos inside.")
        return

    added_count = 0

    for filename in os.listdir(videos_folder):
        if filename.lower().endswith(('.mp4', '.webm', '.mov')):
            # Strip the extension and uppercase it ("a.mp4" -> "A")
            char_text = os.path.splitext(filename)[0].upper()
            
            # Catch bad filenames before they crash the database
            if len(char_text) > 5:
                print(f"⚠️ Skipped '{filename}': Name '{char_text}' is over 5 characters. Rename it to just the letter/number.")
                continue

            file_path = os.path.join(videos_folder, filename)

            # Prevent duplicates
            if FSLSign.objects.filter(char__iexact=char_text).exists():
                print(f"⚠️ Skipped: '{char_text}' already exists in the database.")
                continue

            # Save it
            try:
                with open(file_path, 'rb') as video_file:
                    new_sign = FSLSign(char=char_text)
                    new_sign.media_file.save(filename, File(video_file), save=True)
                    added_count += 1
                    print(f"✅ Success: Uploaded sign for '{char_text}'")
            except Exception as e:
                print(f"❌ Failed to upload '{char_text}': {e}")

    print(f"\n🚀 Done! Successfully added {added_count} new signs to the alphabet dictionary.")

if __name__ == "__main__":
    # Put your A-Z, 0-9 clips in a folder named 'alphabet_clips' in the same directory as this script
    TARGET_FOLDER = "EDITED" 
    
    run_alphabet_upload(TARGET_FOLDER)