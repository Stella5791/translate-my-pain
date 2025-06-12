import json
import re
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load taxonomy and rephrasings
with open("taxonomy.json") as f:
    taxonomy = json.load(f)

with open("rephrasings.json") as f:
    rephrasings = json.load(f)

with open("researcher_notes.json") as f:
    researcher_notes = json.load(f)

GRADUATION = [g.lower() for g in taxonomy.get("graduation_modifiers", [])]
TRIGGERS = [t.lower() for t in taxonomy.get("triggers", [])]
DELIMITERS = r"[^\w']+"


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s']", "", text)
    return text


def generate_ngrams(tokens, max_n=4):
    ngram_list = []
    for n in range(1, max_n + 1):
        ngram_list.extend([" ".join(gram)
                          for gram in zip(*[tokens[i:] for i in range(n)])])
    return ngram_list


def tag_pain_description(text, name=None, duration=None):
    logger.info("User input: %s", text)

    normalized_text = normalize_text(text)
    tokens = re.findall(r"\b[\w']+\b", normalized_text)
    all_ngrams = generate_ngrams(tokens)

    # Convert all n-grams to lowercase
    ngram_set = set([ng.lower() for ng in all_ngrams])

    detected = {
        "metaphors": set(),
        "dimensions": set(),
        "triggers": set(),
        "graduation": set()
    }

    for category, items in taxonomy.get("metaphor_types", {}).items():
        for expression in items.get("expressions", []):
            if expression.lower() in ngram_set:
                detected["metaphors"].add(category)

    for dimension, dim_data in taxonomy.get("metaphor_types", {}).items():
        for word in dim_data.get("dimensions", []):
            if word.lower() in ngram_set:
                detected["dimensions"].add(word.lower())

    for trigger in TRIGGERS:
        if trigger in normalized_text:
            detected["triggers"].add(trigger)

    for grad in GRADUATION:
        if grad in normalized_text:
            detected["graduation"].add(grad)

    # Build clinical summaries
    clinical = {}
    for metaphor in detected["metaphors"]:
        if metaphor in rephrasings:
            clinical[metaphor] = rephrasings[metaphor]

    # Build researcher notes
    research = {}
    for metaphor in detected["metaphors"]:
        if metaphor in researcher_notes:
            research[metaphor] = researcher_notes[metaphor]

    return {
        "metaphors": list(detected["metaphors"]),
        "dimensions": list(detected["dimensions"]),
        "triggers": list(detected["triggers"]),
        "graduation": list(detected["graduation"]),
        "clinical": clinical,
        "research": research,
        "user_info": {
            "name": name,
            "duration": duration
        }
    }
    
    if __name__ == "__main__":