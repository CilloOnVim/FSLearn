import os
import django
import requests
from duckduckgo_search import DDGS
import time
import random

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from learning.models import Word

# --- CONFIGURATION ---
# The absolute path to the folder where you want to dump the pictures.
IMAGE_DIRECTORY = r"C:\Users\cillo\OneDrive\Desktop\IMAGE PICS"

def bulk_download_images():
    print("Starting bulk image download...")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(IMAGE_DIRECTORY):
        os.makedirs(IMAGE_DIRECTORY)

    # Fetch all words from the database
    words = Word.objects.all()
    if not words.exists():
        print("No words found in the database. Run your population script first.")
        return

    # Open DuckDuckGo search session
    with DDGS() as ddgs:
        for word in words:
            # Clean up names like "Me/I" so Windows doesn't think it's a subfolder
            safe_name = word.name.replace("/", "_").replace("\\", "-")
            file_path = os.path.join(IMAGE_DIRECTORY, f"{safe_name}.jpg")

            # Skip if the image is already downloaded
            if os.path.exists(file_path):
                print(f"  [~] Skipped '{safe_name}.jpg' (Already exists)")
                continue

            # I appended "simple illustration" so you don't get stock photos of random people
            search_query = f"{word.name} simple illustration clipart"
            print(f"  [*] Searching for: '{search_query}'...")
            
            try:
                # Get the top 1 image result
                results = list(ddgs.images(search_query, max_results=1))
                
                if not results:
                    print(f"  [-] MISSING: No image found for '{word.name}'")
                    continue
                    
                image_url = results[0]['image']
                
                # Fetch the actual image data
                response = requests.get(image_url, timeout=10)
                response.raise_for_status()
                
                # Force save it as a .jpg regardless of original format
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  [+] Downloaded: {safe_name}.jpg")
                
            except Exception as e:
                print(f"  [-] ERROR: Failed to download '{word.name}'. Reason: {e}")

            # ADD THIS AT THE END OF THE LOOP TO SLOW DOWN THE SCRIPT
            sleep_time = random.uniform(5, 10)
            print(f"  [zZz] Sleeping for {sleep_time:.2f} seconds to avoid rate limits...")
            time.sleep(sleep_time)

if __name__ == "__main__":
    bulk_download_images()