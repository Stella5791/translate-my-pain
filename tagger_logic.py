import json
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

DIMENSIONS = taxonomy.get("dimensions", {})
METAPHOR_TYPES = taxonomy.get("metaphor_types", {})
GRADUATION = taxonomy.get("graduation", {})  # Optional safeguard

stemmer = PorterStemmer()


def stem_list(word_list):
    return [stemmer.stem(w) for w in word_list]


def tag_pain_description(text):
    text_lower = text.lower()
    words = text_lower.split()  # Simpler tokenizer (avoids nltk.download)
    stemmed_input = [stemmer.stem(w) for w in words]

    dimensions = []
    metaphor_matches = {}
    entailments = {}
    graduation_tags = {"maximising": [], "minimising": []}

    # Tag dimensions
    for dim, keywords in DIMENSIONS.items():
        stemmed_keywords = stem_list(keywords)
        if any(stem in stemmed_input for stem in stemmed_keywords):
            dimensions.append(dim)

    # Tag metaphor types
    for mtype, keywords in METAPHOR_TYPES.items():
        stemmed_keywords = stem_list(keywords)
        matched = [kw for kw, skw in zip(
            keywords, stemmed_keywords) if skw in stemmed_input]
        if matched:
            metaphor_matches[mtype] = matched
            entailments[mtype] = keywords

    # Tag graduation (intensifiers)
    for grad_type in ["maximising", "minimising"]:
        keywords = GRADUATION.get(grad_type, [])
        stemmed_keywords = stem_list(keywords)
        matched = [kw for kw, skw in zip(
            keywords, stemmed_keywords) if skw in stemmed_input]
        graduation_tags[grad_type] = matched

    # Fallback message if no descriptors detected
    no_matches = not (
        dimensions or metaphor_matches or graduation_tags["maximising"] or graduation_tags["minimising"])

    return {
        "input": text,
        "dimensions": list(set(dimensions)),
        "metaphor_types": list(metaphor_matches.keys()),
        "matches": metaphor_matches,
        "entailments": entailments,
        "graduation": graduation_tags,
        "note": "No metaphorical or descriptive pain language detected." if no_matches else ""
    }
