# fsl_nlp/nlp_utils.py
import spacy

# Ensure you have the model downloaded: python -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

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

    structure = {
        "time": [],
        "topic": [],           # The Object or focal point
        "comment_subject": [], # The Pronoun/Subject 
        "comment_verb": []     # The Action
    }
    
    # NEW: Memory bank to prevent double-printing words we already combined
    skip_tokens = set()

    for token in doc:
        if token in skip_tokens:
            continue

        word_lemma = token.lemma_.upper()
        
        # 1. Stop Word Filter
        if token.text.lower() in STOP_WORDS:
            continue

        # ==========================================
        # 2. CONTEXTUAL DISAMBIGUATION BLOCK
        # ==========================================
        
        # Disambiguate "LIKE"
        if word_lemma == "LIKE":
            if token.pos_ == "VERB":
                word_lemma = "LIKE (GUSTO)"
            else:
                word_lemma = "LIKE (PAREHO)"

        # Disambiguate Directional "HELP"
        elif word_lemma in ["HELP", "HELPING"]:
            # Look at the words attached to 'help' to find the receiver
            for child in token.children:
                if child.dep_ in ["dobj", "dative", "pobj"]:
                    if child.text.lower() in ["me", "us"]:
                        # Direction is inward (to me)
                        word_lemma = "HELP"
                        skip_tokens.add(child) # Consume 'me' so it doesn't print again
                        break
                    else:
                        # Direction is outward to someone else (you, the girl, the boy). 
                        word_lemma = "HELPING"
                        
                        # CRITICAL: If the object is literally "you", we consume/delete it.
                        # If the object is a noun like "girl", we leave it alone for the Topic.
                        if child.text.lower() == "you":
                            skip_tokens.add(child)
                        break

        # ==========================================

        # 3. Fingerspelling for Proper Nouns
        elif token.ent_type_ == "PERSON":
            word_lemma = f"fs-{word_lemma}" 

        # 4. Time Extraction
        if word_lemma in FORCE_TIME_WORDS or token.ent_type_ in ["TIME", "DATE"]:
            if word_lemma not in structure["time"]: 
                structure["time"].append(word_lemma)
                
        # 5. Topic Extraction (Direct Objects)
        elif token.dep_ in ["dobj", "pobj", "attr"]:
            structure["topic"].append(word_lemma)
            
        # 6. Comment - Subject Extraction
        elif token.dep_ in ["nsubj", "nsubjpass", "prt", "poss"]:
            if word_lemma == "I": 
                word_lemma = "ME"
            if token.text.lower() == "my": 
                word_lemma = "MY"
            structure["comment_subject"].append(word_lemma)
            
        # Included our custom override words here so they get sorted properly
        # 7. Comment - Verb Extraction
        elif token.pos_ in ["VERB", "ADJ", "ROOT"] or token.dep_ == "ROOT" or word_lemma in ["LIKE (GUSTO)", "LIKE (PAREHO)", "HELP", "HELPING"]:
            structure["comment_verb"].append(word_lemma)
        

    time_part = " ".join(structure["time"])
    topic_part = " ".join(structure["topic"])
    comment_part = " ".join(structure["comment_subject"] + structure["comment_verb"])

    # Build the final ordered FSL sequence: Time -> Comment -> Topic
    full_sequence = []
    if time_part:
        full_sequence.append(time_part)
    if comment_part:
        full_sequence.append(comment_part)
    if topic_part:
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


# --- Test Cases ---
if __name__ == "__main__":
    sentences = [
        "I like the museum",
        "It looks like a museum",
        "The teacher is helping me",
        "I am helping you today"
    ]
    
    for s in sentences:
        print(f"English: {s}")
        print(f"FSL Output: {translate_to_fsl(s)['complete']}\n")