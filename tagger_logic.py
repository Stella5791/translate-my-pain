import json
import re
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

# Load clinical rephrasings
with open("clinical_map.json", "r", encoding="utf-8") as f:
    clinical_map = json.load(f)

# Separate metaphor types from graduation modifiers
metaphor_types = {k: v for k, v in taxonomy.items()
                  if k not in ["graduation_modifiers", "life_impact_clues"]}
graduation_modifiers = taxonomy.get("graduation_modifiers", [])
life_impact_clues = taxonomy.get("life_impact_clues", [])

stemmer = PorterStemmer()


def normalize_token(token):
    return re.sub(r"[^\w\s]", "", token.lower().strip())


def generate_ngrams(tokens, min_len=2, max_len=5):
    ngrams = []
    for n in range(min_len, max_len + 1):
        ngrams.extend([" ".join(tokens[i:i+n])
                      for i in range(len(tokens)-n+1)])
    return ngrams


def detect_metaphors(text):
    matches = {}
    entailments = {}
    metaphor_types_found = set()
    dimensions = set()
    graduation = []
    life_impact = []

    raw_text = text.lower()
    tokens = [normalize_token(t) for t in re.split(r"[^\w']+", raw_text)]
    tokens = [t for t in tokens if t]
    ngrams = generate_ngrams(tokens)

    for mtype, meta in metaphor_types.items():
        expressions = meta.get("expressions", [])
        matched = []

        for expr in expressions:
            expr_norm = normalize_token(expr)
            if expr_norm in tokens or expr_norm in ngrams or expr_norm in raw_text:
                matched.append(expr)

        if matched:
            matches[mtype] = matched
            metaphor_types_found.add(mtype)
            entailments[mtype] = meta.get("entailments", [])
            dimensions.update(meta.get("dimensions", []))

    for grad in graduation_modifiers:
        if normalize_token(grad) in tokens:
            graduation.append(grad)

    for clue in life_impact_clues:
        if normalize_token(clue) in raw_text:
            life_impact.append(clue)

    return {
        "matches": matches,
        "entailments": entailments,
        "metaphor_types": list(metaphor_types_found),
        "dimensions": list(dimensions),
        "graduation": graduation,
        "life_impact": life_impact
    }


def tag_pain_description(text):
    text_lower = text.lower()
    result = detect_metaphors(text_lower)

    # Add clinical rephrasings
    if result["metaphor_types"]:
        clinical_rephrasings = {
            mtype: clinical_map.get(mtype, {})
            for mtype in result["metaphor_types"]
        }
    elif result["graduation"]:
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
        "dimensions": sorted(result["dimensions"]),
        "metaphor_types": result["metaphor_types"],
        "matches": result["matches"],
        "entailments": result["entailments"],
        "graduation_only": result["graduation"] if not result["metaphor_types"] else [],
        "impact_context": detect_context(text_lower),
        "life_impact": result["life_impact"],
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
