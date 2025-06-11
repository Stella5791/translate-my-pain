import re
import json
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

# Load clinical rephrasings
with open("clinical_map.json", "r", encoding="utf-8") as f:
    clinical_map = json.load(f)

# Separate metaphor types and graduation modifiers
metaphor_types = {k: v for k, v in taxonomy.items(
) if k not in ["graduation_modifiers", "life_impact_clues"]}
graduation_modifiers = taxonomy.get("graduation_modifiers", [])
life_impact_clues = taxonomy.get("life_impact_clues", [])

stemmer = PorterStemmer()


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text.split()


def generate_ngrams(tokens, max_n=3):
    ngrams = set()
    for n in range(1, max_n + 1):
        for i in range(len(tokens) - n + 1):
            ngram = " ".join(tokens[i:i + n])
            ngrams.add(ngram)
    return ngrams


def detect_context(text):
    triggers = [
        "intercourse", "sex", "penetration", "menstruation", "period", "ovulate", "ovulation",
        "going to the toilet", "urinate", "bowel movement", "defecate", "poop", "wee", "pee",
        "daily life", "getting up", "moving", "walking", "stand", "sit", "sleep", "breathe", "eat"
    ]
    return sorted([t for t in triggers if t in text])


def detect_quality_of_life(text):
    return [phrase for phrase in life_impact_clues if phrase in text]


def tag_pain_description(text):
    text_clean = normalize_text(text)
    ngrams = generate_ngrams(text_clean)
    text_str = " ".join(text_clean)

    matches = {}
    entailments = {}
    dimensions = set()
    graduation_only = []
    qol_impact = detect_quality_of_life(text_str)

    # Metaphor matching
    for mtype, data in metaphor_types.items():
        expressions = data.get("expressions", [])
        matched = [expr for expr in expressions if expr.lower() in ngrams]
        if matched:
            matches[mtype] = matched
            entailments[mtype] = data.get("entailments", [])
            dimensions.update(data.get("dimensions", []))

    # Graduation-only fallback
    if not matches:
        grad_matched = [
            g for g in graduation_modifiers if g.lower() in text_str]
        if grad_matched:
            graduation_only = grad_matched

    # Clinical insights
    if matches:
        clinical_rephrasings = {mtype: clinical_map.get(
            mtype, {}) for mtype in matches}
    elif graduation_only:
        clinical_rephrasings = {
            "graduation_modifiers": {
                "patient_friendly": "Strong, overwhelming descriptors used to convey extreme distress.",
                "likely_mechanism": "Indicative of central sensitization or high pain interference.",
                "clinical_terms": ["pain severity", "pain interference", "functional impact"],
                "literature_framing": ""
            }
        }
    else:
        clinical_rephrasings = {}

    return {
        "input": text,
        "dimensions": sorted(dimensions),
        "metaphor_types": list(matches.keys()),
        "matches": matches,
        "entailments": entailments,
        "graduation_only": graduation_only if not matches else [],
        "impact_context": detect_context(text_str),
        "quality_of_life": qol_impact,
        "clinical_rephrasings": clinical_rephrasings
    }
