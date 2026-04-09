import os
import django
from django.core.files import File

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from learning.models import Theme, Section, Word

# 2. The Data Structure
SIGNS_DATA = {
    "THEME 1: KNOWING WHO WE ARE AND OUR FAMILIES": {
        "Basic Identity": [
            ("Me/I", "Ako"), ("You", "Ikaw"), ("Name", "Pangalan"),
            ("Child", "Bata"), ("Boy", "Lalaki"), ("Girl", "Babae")
        ],
        # ... (Keep the rest of your dictionary here exactly as you have it) ...
        "Daily Activities & Social Skills": [
            ("How are you", "Kamusta"), ("Thank you", "Salamat"), ("Sorry", "Pasensya"),
            ("Hello", "Kumusta"), ("Goodbye", "Paalam")
        ]
    },
    "THEME 2: EXPLORING OUR COMMUNITY": {
        "Values & Character": [
            ("Discipline", "Disiplina"), ("Honesty/Truth", "Katapatan"), ("Respect", "Respeto")
        ]
        # ... (Keep your full THEME 2, 3, and 4 data here) ...
    }
}

def get_video_map_for_theme(theme_folder_path):
    """
    Scans the theme folder and its subfolders. 
    Returns a dictionary mapping the UPPERCASE filename (no extension) to its full path.
    """
    video_map = {}
    if not os.path.exists(theme_folder_path):
        print(f"⚠️ Warning: Folder '{theme_folder_path}' not found.")
        return video_map

    for root, dirs, files in os.walk(theme_folder_path):
        for filename in files:
            if filename.lower().endswith(('.mp4', '.webm', '.mov')):
                base_name = os.path.splitext(filename)[0].upper()
                video_map[base_name] = os.path.join(root, filename)
    return video_map

def sanitize_word_for_filename(word):
    """
    Replaces characters in dictionary words that are illegal in filenames.
    Example: 'Me/I' -> 'ME_I'
    """
    return word.upper().replace('/', '_')

def run():
    print("🚀 Starting database population and video mapping...")
    
    # Get the base directory dynamically for Render compatibility
    BASE_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_VIDEOS_DIR = BASE_SCRIPT_DIR # Change this if your videos are in a subfolder like os.path.join(BASE_SCRIPT_DIR, "videos")

    theme_order = 1
    for theme_title, sections in SIGNS_DATA.items():
        
        # Extract just "THEME 1" from "THEME 1: KNOWING WHO WE ARE..."
        folder_name = theme_title.split(':')[0].strip()
        theme_folder_path = os.path.join(BASE_VIDEOS_DIR, folder_name)
        
        # Pre-scan the videos for this theme to make matching instantaneous
        theme_videos = get_video_map_for_theme(theme_folder_path)

        # Get or create Theme
        theme, t_created = Theme.objects.get_or_create(
            title=theme_title,
            defaults={"order": theme_order}
        )
        if t_created:
            print(f"\n[+] Created Theme: {theme.title}")
        theme_order += 1

        section_order = 1
        for section_title, words in sections.items():
            # Get or create Section
            section, s_created = Section.objects.get_or_create(
                theme=theme,
                title=section_title,
                defaults={"order": section_order}
            )
            if s_created:
                print(f"  [+] Created Section: {section.title}")
            section_order += 1

            word_order = 1
            for english, tagalog in words:
                word_desc = f"Tagalog: {tagalog}. Sign language instructions for '{english}'."
                
                # Figure out what the filename should be
                expected_filename_key = sanitize_word_for_filename(english)

                # Get or create Word (without video first)
                word, w_created = Word.objects.get_or_create(
                    section=section,
                    name=english,
                    defaults={
                        "description": word_desc,
                        "order": word_order
                    }
                )

                if w_created:
                    print(f"    [-] Created Word: {word.name} ({tagalog})")

                # Attach video if it exists in the scanned folder and the word doesn't already have one
                if not word.video and expected_filename_key in theme_videos:
                    video_path = theme_videos[expected_filename_key]
                    filename = os.path.basename(video_path)
                    
                    try:
                        with open(video_path, 'rb') as video_file:
                            word.video.save(filename, File(video_file), save=True)
                            print(f"      ✅ Attached video: {filename}")
                    except Exception as e:
                        print(f"      ❌ Failed to attach video for '{english}': {e}")
                elif not word.video:
                    print(f"      ⚠️ No video found for '{english}' (Expected filename starting with: {expected_filename_key})")

                word_order += 1

    print("\n🏁 Database population and upload complete. Check your Django Admin.")

if __name__ == "__main__":
    run()