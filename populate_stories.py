import os
import django
from django.core.files import File

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fslearn_main.settings') 
django.setup()

from learning.models import Theme, Story, QuizQuestion, QuizChoice

# --- CONFIGURATION ---
# The absolute path to the main folder containing "Story 1", "Story 2", etc.
STORIES_BASE_DIR = r"C:\Users\cillo\OneDrive\Desktop\FSLearn\FSL_STORIES_CUT"

# The data mapping. I generated the wrong answers (False) for you.
STORIES_DATA = [
    {
        "folder_name": "MANO PO LOLA",
        "title": "Mano Po, Lola",
        "theme_search": "THEME 1",
        "description": "Filipino Context: The mano po gesture shows respect for elders. Lola (grandmother) is a central family figure. Pandesal is a classic breakfast bread.\n\nThe Story: Today, I visit my Lola's house. Her house is green. I go to my Lola. I say 'Mano Po.' Lola smiles. She is happy. She gives me food. We eat warm pandesal. I love my Lola.",
        "questions": [
            {"file": "Q1.mp4", "text": "Whose house did I visit?", "choices": [("Lola's", True), ("Tita's", False), ("Friend's", False)]},
            {"file": "Q2.mp4", "text": "What did I say/do to Lola?", "choices": [("Mano Po", True), ("Hello", False), ("Goodbye", False)]},
            {"file": "Q3.mp4", "text": "How did Lola feel?", "choices": [("Happy", True), ("Sad", False), ("Angry", False)]},
            {"file": "Q4.mp4", "text": "What food did we eat?", "choices": [("Pandesal", True), ("Rice", False), ("Candy", False)]},
            {"file": "Q5.mp4", "text": "What color was the house?", "choices": [("Green", True), ("Red", False), ("Blue", False)]},
        ]
    },
    {
        "folder_name": "GOING TO SARI SARI STORE",
        "title": "Going to the Sari-Sari Store",
        "theme_search": "THEME 2",
        "description": "Filipino Context: The sari-sari store is a key part of every Filipino community. Ate (big sister) is a common term.\n\nThe Story: My Ate gives me five pesos. We walk to the store. It is a small sari-sari store. I buy one yellow candy. Ate buys ice. I see a cat sleeping near the store. Our community is nice. We walk home.",
        "questions": [
            {"file": "Q1.mp4", "text": "Who gave me money?", "choices": [("Ate / Big Sister", True), ("Kuya / Big Brother", False), ("Mother", False)]},
            {"file": "Q2.mp4", "text": "Where did we go?", "choices": [("Sari-sari store", True), ("Church", False), ("Park", False)]},
            {"file": "Q3.mp4", "text": "What did I buy?", "choices": [("Candy", True), ("Bread", False), ("Toy", False)]},
            {"file": "Q4.mp4", "text": "What did Ate buy?", "choices": [("Ice", True), ("Water", False), ("Juice", False)]},
            {"file": "Q5.mp4", "text": "What animal was sleeping?", "choices": [("Cat", True), ("Dog", False), ("Bird", False)]},
        ]
    },
    {
        "folder_name": "BIG COLORFUL JEEPNEY",
        "title": "The Big, Colorful Jeepney",
        "theme_search": "THEME 3",
        "description": "Filipino Context: The Jeepney is the 'King of the Road' and a unique national symbol of the Philippines.\n\nThe Story: I am in the street. I see a jeepney. The jeepney is from the Philippines. It is big and long. It has many colors: red, yellow, and blue. Many people get on. The jeepney goes fast. Beep beep!",
        "questions": [
            {"file": "Q1.mp4", "text": "What did I see?", "choices": [("A jeepney", True), ("A bus", False), ("A car", False)]},
            {"file": "Q2.mp4", "text": "The jeepney is from where?", "choices": [("The Philippines", True), ("America", False), ("Japan", False)]},
            {"file": "Q3.mp4", "text": "What colors were on the jeepney?", "choices": [("Red, yellow, blue", True), ("Black and white", False), ("Green and orange", False)]},
            {"file": "Q4.mp4", "text": "How many people?", "choices": [("Many", True), ("Few", False), ("None", False)]},
            {"file": "Q5.mp4", "text": "Was the jeepney fast or slow?", "choices": [("Fast", True), ("Slow", False), ("Not moving", False)]},
        ]
    },
    {
        "folder_name": "LOLA'S ADOBO",
        "title": "Lola's Adobo",
        "theme_search": "THEME 1", # Assuming this fits best here based on your provided list
        "description": "Filipino Context: Adobo is the national dish. Cooking it is an act of love, and it's always eaten with kanin (rice).\n\nThe Story: I am at Lola's house. I smell something good. Lola is cooking. She is cooking adobo! Adobo is food from the Philippines. We eat the adobo with rice. It is delicious! I am full and happy.",
        "questions": [
            {"file": "Q1.mp4", "text": "Who was cooking?", "choices": [("Lola", True), ("Mother", False), ("Ate", False)]},
            {"file": "Q2.mp4", "text": "What was she cooking?", "choices": [("Adobo", True), ("Sinigang", False), ("Pancit", False)]},
            {"file": "Q3.mp4", "text": "What did we eat with the adobo?", "choices": [("Rice", True), ("Bread", False), ("Noodles", False)]},
            {"file": "Q4.mp4", "text": "How did it taste?", "choices": [("Delicious / Good", True), ("Bad", False), ("Sour", False)]},
            {"file": "Q5.mp4", "text": "How did I feel?", "choices": [("Full / Happy", True), ("Hungry", False), ("Sad", False)]},
        ]
    },
    {
        "folder_name": "BRGY CLEAN UP",
        "title": "Barangay Clean-Up",
        "theme_search": "THEME 4",
        "description": "Filipino Context: The barangay is the local community unit. Bayanihan (community spirit) and using a walis (broom) are culturally specific.\n\nThe Story: It is Saturday morning. My family helps clean our barangay. My father has a walis (broom). I have a big trash bag. We pick up paper and plastic bottles. Now, our barangay is clean and beautiful. I am happy to help.",
        "questions": [
            {"file": "Q1.mp4", "text": "When did we clean?", "choices": [("Saturday", True), ("Monday", False), ("Sunday", False)]},
            {"file": "Q2.mp4", "text": "Where did we clean?", "choices": [("The barangay", True), ("The school", False), ("The house", False)]},
            {"file": "Q3.mp4", "text": "What did my father have?", "choices": [("Walis / Broom", True), ("Mop", False), ("Water", False)]},
            {"file": "Q4.mp4", "text": "What did I have?", "choices": [("Trash bag", True), ("Bucket", False), ("Box", False)]},
            {"file": "Q5.mp4", "text": "What did we pick up?", "choices": [("Paper / Bottles / Trash", True), ("Food", False), ("Leaves", False)]},
        ]
    }
]

def run():
    print("Starting Story and Quiz population...")

    for data in STORIES_DATA:
        # 1. Find the Theme
        theme = Theme.objects.filter(title__icontains=data["theme_search"]).first()
        if not theme:
            print(f"[-] ERROR: Could not find a theme matching '{data['theme_search']}'. Skipping {data['title']}.")
            continue

        # 2. Get or Create the Story
        story, s_created = Story.objects.get_or_create(
            title=data["title"],
            theme=theme,
            defaults={"description": data["description"]}
        )
        if s_created:
            print(f"\n[+] Created Story: {story.title}")
        else:
            print(f"\n[~] Found existing Story: {story.title}")

        # 3. Attach the main STORY video
        story_video_path = os.path.join(STORIES_BASE_DIR, data["folder_name"], "STORY.mp4")
        if not story.video and os.path.exists(story_video_path):
            with open(story_video_path, 'rb') as f:
                story.video.save(f"STORY_{data['folder_name'].replace(' ', '')}.mp4", File(f), save=True)
            print("  [+] Attached STORY.mp4")
        elif not os.path.exists(story_video_path):
            print(f"  [-] MISSING: Main story video not found at {story_video_path}")

        # 4. Process the Questions
        for q_data in data["questions"]:
            question, q_created = QuizQuestion.objects.get_or_create(
                story=story,
                text=q_data["text"]
            )
            
            # Attach the Question video (Q1.mp4, etc.)
            q_video_path = os.path.join(STORIES_BASE_DIR, data["folder_name"], q_data["file"])
            if not question.video and os.path.exists(q_video_path):
                with open(q_video_path, 'rb') as f:
                    question.video.save(f"{data['folder_name'].replace(' ', '')}_{q_data['file']}", File(f), save=True)
                print(f"    [+] Created Question and attached {q_data['file']}: {question.text}")
            elif not os.path.exists(q_video_path):
                print(f"    [-] MISSING VIDEO for Question: {question.text} (Expected {q_video_path})")

            # 5. Process the Choices
            if q_created: # Only create choices if the question was just created to avoid duplicates
                for choice_text, is_correct in q_data["choices"]:
                    QuizChoice.objects.create(
                        question=question,
                        text=choice_text,
                        is_correct=is_correct
                    )

if __name__ == "__main__":
    run()