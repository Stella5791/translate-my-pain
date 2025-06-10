import json
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

# Load clinical rephrasings
with open("clinical_map.json", "r", encoding="utf-8") as f:
    CLINICAL_MAP = json.load(f)

# Pull metaphor types, graduation, and dimensions
METAPHOR_TYPES = {k: v for k, v in taxonomy.items() if k not in [
    "graduation_modifiers"]}
GRADUATION = taxonomy.get("graduation_modifiers", [])
stemmer = PorterStemmer()


def stem_list(word_list):
    return [stemmer.stem(w) for w in word_list]


def tag_pain_description(text):
    text_lower = text.lower()
    words = text_lower.split()  # Simple tokenizer
    stemmed_input = [stemmer.stem(w) for w in words]

    dimensions = set()
    metaphor_matches = {}
    entailments = {}
    graduation_tags = []

    # Tag metaphor types
    for mtype, data in METAPHOR_TYPES.items():
        expressions = data.get("expressions", [])
        stemmed_expr = stem_list(expressions)
        matched = [expr for expr, sexpr in zip(
            expressions, stemmed_expr) if sexpr in stemmed_input]
        if matched:
            metaphor_matches[mtype] = matched
            entailments[mtype] = data.get("entailments", [])
            dimensions.update(data.get("dimensions", []))

    # Graduation intensifiers
    stemmed_grads = stem_list(GRADUATION)
    graduation_tags = [g for g, sg in zip(
        GRADUATION, stemmed_grads) if sg in stemmed_input]

    # Clinical info fallback
    clinical_descriptions = (
        {mtype: CLINICAL_MAP.get(mtype, {}) for mtype in metaphor_matches}
        if metaphor_matches else
        {"graduation_modifiers": {
            "patient_friendly": "Strong, overwhelming descriptors used to convey extreme distress.",
            "likely_mechanism": "Indicative of central sensitization or high pain interference.",
            "clinical_terms": ["pain severity", "pain interference", "functional impact"]
        }} if graduation_tags else {}
    )

    return {
        "input": text,
        "dimensions": sorted(dimensions),
        "metaphor_types": list(metaphor_matches.keys()),
        "matches": metaphor_matches,
        "entailments": entailments,
        "graduation_only": graduation_tags if metaphor_matches == {} else [],
        "clinical_rephrasings": clinical_descriptions
    }
