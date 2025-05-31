import json
import re

# Load taxonomy from taxonomy.json
with open("taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy = json.load(f)

DIMENSIONS = taxonomy["dimensions"]
METAPHOR_TYPES = taxonomy["metaphor_types"]


def tag_pain_description(text):
    text_lower = text.lower()
    dimensions = []
    metaphor_types = []
    entailments = []

    # Tag dimensions
    for dim, keywords in DIMENSIONS.items():
        if any(word in text_lower for word in keywords):
            dimensions.append(dim)

    # Tag metaphor types
    for mtype, keywords in METAPHOR_TYPES.items():
        if any(word in text_lower for word in keywords):
            metaphor_types.append(mtype)

    # Add entailments for matched metaphor types
    for mtype in metaphor_types:
        # optional: map to curated entailments
        entailments.extend(METAPHOR_TYPES[mtype])

    return {
        "input": text,
        "dimensions": list(set(dimensions)),
        "metaphor_types": list(set(metaphor_types)),
        "entailments": list(set(entailments))
    }
