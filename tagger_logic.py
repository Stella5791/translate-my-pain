import json
import re
from itertools import tee
from nltk.stem import PorterStemmer

# === Load Taxonomy and Clinical Rephrasings ===

with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

with open("clinical_map.json", "r", encoding="utf-8") as f:
    clinical_map = json.load(f)

metaphor_types = {k: v for k, v in taxonomy.items() if k !=
                  "graduation_modifiers"}
graduation_modifiers = taxonomy.get("graduation_modifiers", [])

stemmer = PorterStemmer()

# === Token Normalization and N-gram Generation ===


def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().split()


def generate_ngrams(tokens, n=3):
    def window(seq, n):
        iters = tee(seq, n)
        for i, it in enumerate(iters):
            for _ in range(i):
                next(it, None)
        return zip(*iters)

    ngrams = []
    for i in range(1, n + 1):
        for gram in window(tokens, i):
            ngrams.append(" ".join(gram))
    return ngrams


def stem_list(phrases):
    return [" ".join(stemmer.stem(w) for w in phrase.split()) for phrase in phrases]

# === Contextual Triggers (Life Impact) ===


triggers = [
    "intercourse", "sex", "penetration", "menstruation", "period", "ovulate", "ovulation",
    "going to the toilet", "urinate", "bowel movement", "defecate", "poop", "wee", "pee",
    "daily life", "getting up", "moving", "walking", "stand", "sit", "sleep", "breathe", "eat"
]


def detect_context(text):
    return sorted([t for t in triggers if t in text])

# === Main Function ===


def tag_pain_description(text):
    text_lower = text.lower()
    tokens = normalize_text(text_lower)
    all_phrases = generate_ngrams(tokens)
    stemmed_phrases = stem_list(all_phrases)

    matches = {}
    entailments = {}
    dimensions = set()
    graduation_only = []

    # === Match metaphor expressions ===
    for mtype, data in metaphor_types.items():
        expressions = data.get("expressions", [])
        stemmed_expr = stem_list(expressions)

        matched = [expr for expr, stemmed in zip(
            expressions, stemmed_expr) if stemmed in stemmed_phrases]
        if matched:
            matches[mtype] = matched
            entailments[mtype] = data.get("entailments", [])
            dimensions.update(data.get("dimensions", []))

    # === Match standalone graduation modifiers (if no metaphors matched) ===
    if not matches:
        stemmed_grads = stem_list(graduation_modifiers)
        graduation_only = [word for word, s in zip(
            graduation_modifiers, stemmed_grads) if s in stemmed_phrases]

    # === Clinical Rephrasings ===
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
