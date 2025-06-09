import json
from nltk.stem import PorterStemmer

# Load taxonomy
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

DIMENSIONS = taxonomy["dimensions"]
METAPHOR_TYPES = taxonomy["metaphor_types"]

stemmer = PorterStemmer()


def stem_list(word_list):
    return [stemmer.stem(w) for w in word_list]


def tag_pain_description(text):
    text_lower = text.lower()
    words = text_lower.split()  # simpler tokenizer that avoids nltk.download
    stemmed_input = [stemmer.stem(w) for w in words]

    dimensions = []
    metaphor_matches = {}
    entailments = {}

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

    return {
        "input": text,
        "dimensions": list(set(dimensions)),
        "metaphor_types": list(metaphor_matches.keys()),
        "matches": metaphor_matches,
        "entailments": entailments
    }
