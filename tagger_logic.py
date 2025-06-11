import json
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

# Load clinical rephrasings
with open("clinical_map.json", "r", encoding="utf-8") as f:
    clinical_map = json.load(f)

# Separate metaphor types from graduation modifiers
metaphor_types = {k: v for k, v in taxonomy.items() if k !=
                  "graduation_modifiers"}
graduation_modifiers = taxonomy.get("graduation_modifiers", [])

stemmer = PorterStemmer()


def stem_list(words):
    return [stemmer.stem(word) for word in words]


def tag_pain_description(text):
    text_lower = text.lower()
    words = text_lower.split()
    stemmed_input = [stemmer.stem(word) for word in words]

    matches = {}
    entailments = {}
    dimensions = set()
    graduation_only = []

    # Match metaphor expressions
    for mtype, data in metaphor_types.items():
        expressions = data.get("expressions", [])
        stemmed_expr = stem_list(expressions)

        matched = [expr for expr, stemmed in zip(
            expressions, stemmed_expr) if stemmed in stemmed_input]
        if matched:
            matches[mtype] = matched
            entailments[mtype] = data.get("entailments", [])
            dimensions.update(data.get("dimensions", []))

    # Match standalone graduation modifiers (only if no metaphor matches)
    if not matches:
        stemmed_grads = stem_list(graduation_modifiers)
        graduation_only = [word for word, s in zip(
            graduation_modifiers, stemmed_grads) if s in stemmed_input]

    # Clinical info
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
        "impact_context": detect_context(text_lower),
        "clinical_rephrasings": clinical_rephrasings
    }


# Pain context clues (e.g., activity-related triggers)
triggers = [
    "intercourse", "sex", "penetration", "menstruation", "period", "ovulate", "ovulation",
    "going to the toilet", "urinate", "bowel movement", "defecate", "poop", "wee", "pee",
    "daily life", "getting up", "moving", "walking", "stand", "sit", "sleep", "breathe", "eat"
]


def detect_context(text_lower):
    return sorted([t for t in triggers if t in text_lower])
