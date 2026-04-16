import os
import sys
import argparse
import django
from django.core.files import File

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings')
django.setup()

from learning.models import Word

def bulk_upload_images(image_directory):
    print("Initializing Bulk Image Upload Sequence for FSL Words...")
    
    if not os.path.exists(image_directory):
        print(f"[X] FATAL ERROR: The folder '{image_directory}' was not found.")
        print("Please provide a valid folder path containing the images.")
        return

    # Fetch all words from the database
    words = Word.objects.all()
    if not words.exists():
        print("[X] No words found in the database. Add words first.")
        return

    added_count = 0
    skipped_count = 0
    failed_count = 0

    for word in words:
        # Reconstruct the safe name used during download
        safe_name = word.name.replace("/", "_").replace("\\", "-")
        filename = f"{safe_name}.jpg"
        file_path = os.path.join(image_directory, filename)

        if not os.path.exists(file_path):
            print(f"[-] MISSING FILE: '{filename}' not found for word '{word.name}'. Skipping.")
            skipped_count += 1
            continue

        try:
            # Open the image and save it to the image field of the Word model
            with open(file_path, 'rb') as img_file:
                # This automatically uploads the file to 'words/images/' and saves the model
                word.image.save(filename, File(img_file), save=True)
                added_count += 1
                print(f"[+] SUCCESS: Image attached to '{word.name}' (Section: {word.section.title}, Theme: {word.section.theme.title})")
        except Exception as e:
            print(f"[X] ERROR: Failed to upload image for '{word.name}': {e}")
            failed_count += 1

    print("\n" + "="*40)
    print("BULK IMAGE UPLOAD COMPLETE")
    print(f"Successfully Updated: {added_count} words")
    print(f"Skipped (No local image found): {skipped_count} words")
    print(f"Failed: {failed_count} words")
    print("="*40 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bulk upload images to FSL words.')
    parser.add_argument('folder', type=str, help='Absolute path to the folder containing all the images')
    args = parser.parse_args()
    
    bulk_upload_images(args.folder)
