import os
import django
from django.core.files import File

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from learning.models import Theme, Word

# --- CONFIGURATION ---
# Change this string to run the script for a different theme later.
TARGET_THEME = "THEME 1: KNOWING WHO WE ARE AND OUR FAMILIES"

# The absolute path to the folder containing your MP4 files. 
# Use the 'r' prefix so Windows backslashes don't break the string.
VIDEO_DIRECTORY = r"C:\Users\cillo\OneDrive\Desktop\FSL_WORDS\THEME 1"

def attach_videos():
    print(f"Targeting Theme: {TARGET_THEME}")
    
    try:
        theme = Theme.objects.get(title=TARGET_THEME)
    except Theme.DoesNotExist:
        print("Error: Theme not found. Check your spelling or run the population script first.")
        return

    # Grab every word linked to a section inside this specific theme
    words = Word.objects.filter(section__theme=theme)
    
    if not words.exists():
        print("No words found for this theme.")
        return

    print(f"Found {words.count()} words. Scanning directory for matches...")

    success_count = 0
    missing_count = 0

    for word in words:
        # Skip if it already has a video so you don't overwrite things if you run this twice
        if word.video:
            print(f"  [~] Skipped '{word.name}' (Video already exists)")
            continue

        # The script will try to find a file matching any of these names
        filenames_to_try = [
            f"{word.name}.mp4",                     # e.g., Happy.mp4
            f"{word.name.lower()}.mp4",             # e.g., happy.mp4
            f"{word.slug}.mp4",                     # e.g., happy-masaya.mp4
            f"{word.name.replace('/', '_')}.mp4",   # e.g., Me_I.mp4
            f"{word.name.replace('/', '-')}.mp4"    # e.g., Me-I.mp4
        ]

        file_found = False
        for filename in filenames_to_try:
            file_path = os.path.join(VIDEO_DIRECTORY, filename)
            
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    # Passing True at the end automatically saves the model
                    word.video.save(filename, File(f), save=True)
                
                print(f"  [+] Attached '{filename}' to Word: {word.name}")
                success_count += 1
                file_found = True
                break # Stop searching once a match is found
        
        if not file_found:
            print(f"  [-] MISSING: Could not find a video for '{word.name}'. Expected e.g., {filenames_to_try[0]} or {filenames_to_try[2]}")
            missing_count += 1

    print("\n--- Execution Summary ---")
    print(f"Successfully attached: {success_count}")
    print(f"Missing files: {missing_count}")

if __name__ == "__main__":
    attach_videos()