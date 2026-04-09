import os
import shutil

# The exact 62 words from your image, read left-to-right, row-by-row.
# All caps to match your nlp_utils.py output requirements.
FSL_WORDS = [
    # Row 1
    "BOY", "BRING HERE", "BRING THERE", "CLEAN", "CLOSE", "COME", "COUNT", "DO", "DRAW", "DRINK", "DRIVE", "EAT", "FINISH",
    # Row 2
    "FOLLOW", "GET", "GIRL", "GIVE ME", "GIVE YOU", "GO", "HAVE", "HELP", "HELPING ME", "HELPING YOU", "HELPING", "HOLD", "KNOW",
    # Row 3
    "LATER", "LEARN", "LIKE (GUSTO)", "LIKE (PAREHO)", "LISTEN", "LOOK", "MAKE", "MY", "NOW", "OBSERVE", "OPEN", "PLANT (HALAMAN)", "PLANT (TANIM)",
    # Row 4
    "PROTECT", "READ", "SAY", "SEE", "SHOW (ME)", "SHOW (YOU)", "TAKE CARE", "TAKE", "TELL ME", "TELL", "THEY", "THROW AWAY", "TODAY",
    # Row 5
    "TOMORROW", "TONIGHT", "USE", "VISIT", "WANT", "WATCH", "WATER", "WATERING", "WE", "YESTERDAY"
]

def batch_rename_videos(target_directory):
    # 1. Grab all mp4 files in the directory, excluding any script files
    raw_files = [f for f in os.listdir(target_directory) if f.endswith('.mp4') or f.endswith('.mov')]
    
    # 2. Sort them alphanumerically (Make sure your camera named them sequentially like VID_001, VID_002, etc.)
    raw_files.sort()

    if len(raw_files) != len(FSL_WORDS):
        print(f"CRITICAL WARNING, GOAT: You have {len(raw_files)} videos in the folder, but {len(FSL_WORDS)} words in the array.")
        print("The script will still run, but check your files to make sure they match up.")

    # 3. Create a safe output folder so we don't destroy the originals
    output_dir = os.path.join(target_directory, "renamed_ready")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 4. Copy and rename
    for index, old_filename in enumerate(raw_files):
        if index >= len(FSL_WORDS):
            break # Stop if we have more videos than words
            
        new_name = f"{FSL_WORDS[index]}.mp4"
        
        old_path = os.path.join(target_directory, old_filename)
        new_path = os.path.join(output_dir, new_name)
        
        shutil.copy2(old_path, new_path)
        print(f"Success: {old_filename} -> {new_name}")

    print(f"\nDone. Check the '{output_dir}' folder.")

if __name__ == "__main__":
    # Runs in the current folder where the script is located
    current_folder = os.getcwd()
    batch_rename_videos(current_folder)
