# student/nlp_utils.py
import spacy

nlp = spacy.load("en_core_web_sm")

# ... (Keep your FORCE_TIME_WORDS set here) ...
FORCE_TIME_WORDS = {
    "MORNING", "AFTERNOON", "EVENING", "NIGHT", "NOON", "NOW",
    "TODAY", "TOMORROW", "YESTERDAY", "TONIGHT", "SUNDAY", "MONDAY",
    "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY",
    "DAY", "WEEK", "MONTH", "YEAR", "EVERY",
}

def translate_to_fsl(english_sentence):
    doc = nlp(english_sentence)

    structure = {
        "question": [], "time": [], "object": [],
        "subject": [], "action": [], "negation": [],
    }

    for token in doc:
        word_lemma = token.lemma_.upper()

        # 1. Skip Stop Words
        if token.text.lower() in ["the", "a", "an", "to", "is", "are", "am", "do", "does", "of", "in", "on", "at"]:
            continue

        # --- NEW: NAME DETECTION LOGIC ---
        # If Spacy thinks this is a Person, force fingerspelling tag
        if token.ent_type_ == "PERSON":
            word_lemma = f"fs-{word_lemma}" 

        # 2. Classification Logic
        if word_lemma in FORCE_TIME_WORDS:
            structure["time"].append(word_lemma)
        elif token.tag_ in ["WDT", "WP", "WRB"]:
            structure["question"].append(word_lemma)
        elif token.ent_type_ in ["TIME", "DATE"] or token.dep_ == "npadvmod":
            structure["time"].append(word_lemma)
        elif token.dep_ == "neg":
            structure["negation"].append(word_lemma)
        elif token.dep_ in ["dobj", "pobj", "attr"] or (token.dep_ == "nsubj" and token.head.pos_ == "ADJ"):
            structure["object"].append(word_lemma)
        elif token.dep_ in ["nsubj", "nsubjpass", "prt", "poss"]:
            if word_lemma == "I": word_lemma = "ME"
            if token.text.lower() == "my": word_lemma = "MY"
            structure["subject"].append(word_lemma)
        elif token.pos_ in ["VERB", "ADJ", "ADV"] and token.dep_ != "npadvmod":
            structure["action"].append(word_lemma)
        else:
            # Catch-all
            structure["action"].append(word_lemma)

    def join_or_none(lst):
        return " ".join(lst) if lst else ""

    time_part = join_or_none(structure["question"] + structure["time"])
    topic_part = join_or_none(structure["object"])
    comment_part = join_or_none(structure["subject"] + structure["action"] + structure["negation"])

    full_sequence = []
    if structure["question"] or structure["time"]:
        full_sequence.extend(structure["question"] + structure["time"])
    if structure["subject"] or structure["action"] or structure["negation"]:
        full_sequence.extend(structure["subject"] + structure["action"] + structure["negation"])
    if structure["object"]:
        full_sequence.extend(structure["object"])

    complete_output = " ".join(full_sequence)
    
    return {
        "time": time_part,
        "topic": topic_part,
        "comment": comment_part,
        "complete": complete_output
    }