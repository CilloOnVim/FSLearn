import spacy
from student.models import FSLWord

# Ensure you have the model downloaded: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

# --- CUSTOM ENTITY RULER FOR HISTORICAL NAMES ---
if not nlp.has_pipe("entity_ruler"):
    ruler = nlp.add_pipe("entity_ruler", before="ner")
    
    # Add all your custom historical figures or special names here
    patterns = [
        {"label": "PERSON", "pattern": [{"LOWER": "andres"}, {"LOWER": "bonifacio"}]},
        {"label": "PERSON", "pattern": [{"LOWER": "jose"}, {"LOWER": "rizal"}]},
        {"label": "PERSON", "pattern": [{"LOWER": "apolinario"}, {"LOWER": "mabini"}]}
    ]
    ruler.add_patterns(patterns)
# -------------------------------------------------

STOP_WORDS = {
    "the", "a", "an", "to", "is", "are", "am", "was", "were", 
    "do", "does", "did", "of", "in", "on", "at"
}

FORCE_TIME_WORDS = {
    "MORNING", "AFTERNOON", "EVENING", "NIGHT", "NOON", "NOW",
    "TODAY", "TOMORROW", "YESTERDAY", "TONIGHT", "SUNDAY", "MONDAY",
    "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY",
    "DAY", "WEEK", "MONTH", "YEAR", "EVERY",
}

def translate_to_fsl(english_sentence):
    doc = nlp(english_sentence)

    # Merge named entities so names like "John Smith" become a single token
    with doc.retokenize() as retokenizer:
        for ent in doc.ents:
            retokenizer.merge(ent)

    structure = {
        "time": [],
        "topic": [],           # The Object or focal point
        "comment_subject": [], # The Pronoun/Subject 
        "comment_verb": []     # The Action
    }
    
    skip_tokens = set()

    for token in doc:
        if token in skip_tokens:
            continue

        word_lemma = token.lemma_.upper()

        # --- EXCEPTION PATCH: Protect 'Philippines' from being lemmatized ---
        if token.text.lower() == "philippines":
            word_lemma = "PHILIPPINES"
        # --------------------------------------------------------------------
        
        # 1. Stop Word Filter
        if token.text.lower() in STOP_WORDS:
            continue

        # ==========================================
        # 2. CONTEXTUAL DISAMBIGUATION BLOCK
        # ==========================================
        
        if word_lemma == "LIKE":
            if token.pos_ == "VERB":
                word_lemma = "LIKE (GUSTO)"
            else:
                word_lemma = "LIKE (PAREHO)"

        elif word_lemma in ["HELP", "HELPING"]:
            for child in token.children:
                if child.dep_ in ["dobj", "dative", "pobj"]:
                    if child.text.lower() in ["me", "us"]:
                        word_lemma = "HELP"
                        skip_tokens.add(child)
                        break
                    else:
                        word_lemma = "HELPING"
                        if child.text.lower() == "you":
                            skip_tokens.add(child)
                        break

        # ==========================================
        # 3. Handle Proper Nouns (Tag them, don't shred them yet)
        elif token.ent_type_ == "PERSON":
            # Turns "Jose Rizal" into "name-JOSE_RIZAL" so it survives the string split later
            word_lemma = f"name-{token.text.upper().replace(' ', '_')}"

        # 4. Time Extraction
        if word_lemma in FORCE_TIME_WORDS or token.ent_type_ in ["TIME", "DATE"]:
            if word_lemma not in structure["time"]: 
                structure["time"].append(word_lemma)
                
        # ==========================================
        # 5. Topic Extraction (Objects & their Adjectives)
        # ==========================================
        elif token.dep_ in ["dobj", "pobj", "attr", "dative", "nummod"] or (token.pos_ == "ADJ" and token.dep_ == "amod" and token.head.dep_ in ["dobj", "pobj", "attr", "dative"]):
            if word_lemma == "I": 
                word_lemma = "ME"
            structure["topic"].append(word_lemma)
            
        # ==========================================
        # 6. Comment - Subject Extraction (Subjects & their Adjectives)
        # ==========================================
        elif token.dep_ in ["nsubj", "nsubjpass", "poss"] or (token.pos_ == "ADJ" and token.dep_ == "amod" and token.head.dep_ in ["nsubj", "nsubjpass"]):
            if word_lemma == "I": 
                word_lemma = "ME"
            if token.text.lower() == "my": 
                word_lemma = "MY"
            structure["comment_subject"].append(word_lemma)
            
        # ==========================================
        # 7. Comment - Verb Extraction (Actions & Predicate Adjectives)
        # ==========================================
        elif token.pos_ in ["VERB", "ROOT"] or token.dep_ in ["ROOT", "prt", "acomp"] or word_lemma in ["LIKE (GUSTO)", "LIKE (PAREHO)", "HELP", "HELPING"]:
            structure["comment_verb"].append(word_lemma)
            
    # ==========================================
    # 8. FSL REDUNDANCY & POSSESSIVE CLEANUP
    # ==========================================
    # FSL drops possessive pronouns when the subject is already established.
    # This prevents Signed Exact English (SEE) and stops fingerspelling fallbacks.
    possessives_to_drop = ["HIS", "HER", "ITS", "THEIR", "OUR"]

    # Handle the "MY" redundancy (if "ME" is present)
    has_me = "ME" in structure["comment_subject"] or "ME" in structure["topic"]
    if has_me and "MY" in structure["comment_subject"]:
        structure["comment_subject"] = [word for word in structure["comment_subject"] if word != "MY"]

    # Purge all 3rd-person possessives from the arrays
    structure["comment_subject"] = [word for word in structure["comment_subject"] if word not in possessives_to_drop]
    structure["topic"] = [word for word in structure["topic"] if word not in possessives_to_drop]

    time_part = " ".join(structure["time"])
    topic_part = " ".join(structure["topic"])
    comment_part = " ".join(structure["comment_subject"] + structure["comment_verb"])

    # ==========================================
    # FSL TIME-COMMENT-TOPIC SYNTAX
    # ==========================================
    full_sequence = []
    if time_part:
        full_sequence.append(time_part)
    if comment_part: # Comment (Subject + Verb) comes BEFORE Topic
        full_sequence.append(comment_part)
    if topic_part:  # Topic (Object) comes LAST
        full_sequence.append(topic_part)

    complete_output = " ".join(full_sequence)

    return {
        "time": time_part,
        "comment_subject": " ".join(structure["comment_subject"]), 
        "comment_verb": " ".join(structure["comment_verb"]),       
        "topic": topic_part,
        "comment": comment_part,
        "complete": complete_output
    }


# --- QUIZ VALIDATOR HELPER ---
def validate_quiz_sentence(sentence):
    """
    Analyzes a sentence for the quiz generator, checking if all words
    have corresponding videos in the database.
    """
    nlp_result = translate_to_fsl(sentence)
    
    analysis_report = []
    words_to_check = []
    
    def process_slot(text_block, category_name):
        if text_block:
            for word in text_block.split():
                clean_word = word.strip(".,!?")
                if clean_word:
                    words_to_check.append((clean_word, category_name))

    # Processes in the exact FSL order: Time -> Comment (Subject -> Action) -> Topic
    process_slot(nlp_result.get('time'), 'Time')
    process_slot(nlp_result.get('comment_subject'), 'Subject')
    process_slot(nlp_result.get('comment_verb'), 'Action')
    process_slot(nlp_result.get('topic'), 'Topic')

    all_good = True

    for word_text, category in words_to_check:
        # 1. Handle Explicit Fingerspelling
        if word_text.startswith("fs-"):
            exists = True
            display_word = word_text.replace("fs-", "") + " (Fingerspell)"
            
        # 2. Handle Name Tags (So it doesn't break on "Jose Rizal")
        elif word_text.startswith("name-"):
            clean_name = word_text.replace("name-", "").replace("_", " ")
            exists = FSLWord.objects.filter(word__iexact=clean_name).exists()
            display_word = clean_name
            if not exists:
                all_good = False
                
        # 3. Standard Vocabulary
        else:
            exists = FSLWord.objects.filter(word__iexact=word_text).exists()
            display_word = word_text
            if not exists:
                all_good = False
        
        analysis_report.append({
            "word": display_word,
            "category": category,
            "has_video": exists
        })

    return {
        "nlp_result": nlp_result,
        "report": analysis_report,
        "all_good": all_good
    }