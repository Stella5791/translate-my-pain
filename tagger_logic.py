import re
import json
from entailments import get_entailments

DELIMITERS = r"[\s.,;!?()\[\]{}<>\n\t]+"

with open('taxonomy.json') as f:
    taxonomy = json.load(f)

GRADUATION = taxonomy.get("graduation_modifiers", [])
TRIGGERS = taxonomy.get("triggers", [])
LIFE_IMPACT_CLUES = taxonomy.get("life_impact_clues", [])


def tokenize(text):
    return re.split(DELIMITERS, text.lower())


def detect_metaphors(text):
    matches = {}
    metaphor_types = set()
    entailments = {}
    dimensions = set()
    text_lower = text.lower()

    for key, data in taxonomy.get("metaphor_types", {}).items():
        for expr in data.get("expressions", []):
            expr_lower = expr.lower()
            pattern = r'\\b' + re.escape(expr_lower) + r'\\b'
            if re.search(pattern, text_lower):
                matches.setdefault(key, []).append(expr)
                metaphor_types.add(key)
                entailments[key] = get_entailments(key)

    print("DEBUG - Metaphor matches:", matches)  # Debugging line
    print("DEBUG - Entailments:", entailments)   # Debugging line
    return matches, entailments, list(metaphor_types)


def generate_entailment_summary(entailments):
    if not entailments:
        return "\U0001FAE2 Your pain holds meaning, but no specific metaphor patterns were identified this time."

    intro = "\U0001FAE2 Your pain communicates layers of meaning:"
    sentences = []

    for category, items in entailments.items():
        human_category = category.replace('_', ' ').capitalize()
        if items:
            if len(items) == 1:
                phrase = items[0]
            elif len(items) == 2:
                phrase = f"{items[0]} and {items[1]}"
            else:
                phrase = f"{', '.join(items[:-1])}, and {items[-1]}"

            sentence = f"It speaks of {phrase.lower()} — often associated with {human_category}."
            sentences.append(sentence)

    return intro + " " + " ".join(sentences)


def get_clinical_info(text):
    return "\U0001FA7A Based on your description, your pain may involve symptoms that suggest underlying inflammation, nerve sensitivity, or muscular tension. These expressions point to functional disruption and emotional distress, and should be discussed with a healthcare provider to explore appropriate evaluation and support."


def get_research_notes(text):
    return "\U0001F4DA The metaphors you've used reflect a rich semantic field of embodied suffering. This type of language provides valuable insights into how patients conceptualize chronic pain beyond clinical terminology, supporting a person-centered approach to qualitative health research."


def tag_pain_description(text, name=None, duration=None):
    matches, entailments, metaphor_types = detect_metaphors(text)

    return {
        "user_info": {
            "name": name,
            "duration": duration
        },
        "input": text,
        "plain_summary": generate_entailment_summary(entailments),
        "clinical_rephrasings": get_clinical_info(text),
        "research": get_research_notes(text),
        "entailments": entailments
    }


def generate_patient_summary(results):
    return results.get("plain_summary", "")


def generate_doctor_summary(results):
    return results.get("clinical_rephrasings", "")


def generate_research_summary(results):
    return results.get("research", "")
