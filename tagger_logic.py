import json
import re
import logging
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load taxonomy and rephrasings
with open("taxonomy.json") as f:
    taxonomy = json.load(f)

with open("rephrasings.json") as f:
    rephrasings = json.load(f)

GRADUATION = taxonomy.get("graduation_modifiers", [])
DELIMITERS = r"[^\w']+"
TRIGGERS = taxonomy.get("triggers", [])


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s']", "", text)
    return text


def generate_ngrams(tokens, max_n=4):
    ngram_list = []
    for n in range(1, max_n + 1):
        ngram_list.extend([" ".join(gram) for gram in ngrams(tokens, n)])
    return ngram_list


def tag_pain_description(text):
    logger.info("User input: %s", text)

    normalized_text = normalize_text(text)
    tokens = word_tokenize(normalized_text)
    all_ngrams = generate_ngrams(tokens)

    detected = {
        "metaphors": set(),
        "dimensions": set(),
        "triggers": set(),
        "graduation": set()
    }

    for category, items in taxonomy.get("metaphor_types", {}).items():
        for expression in items:
            if expression in all_ngrams:
                detected["metaphors"].add(category)

    for dimension, items in taxonomy.get("dimensions", {}).items():
        for word in items:
            if word in all_ngrams:
                detected["dimensions"].add(dimension)

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

    return {
        "metaphors": list(detected["metaphors"]),
        "dimensions": list(detected["dimensions"]),
        "triggers": list(detected["triggers"]),
        "graduation": list(detected["graduation"]),
        "clinical": clinical
    }


if __name__ == "__main__":
    test_text = "It feels like a thousand knives are stabbing my uterus."
    print(tag_pain_description(test_text))
