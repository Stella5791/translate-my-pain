from pain_descriptor_auto_tagger import classify_descriptor_rulebased
from entailments import get_entailments


def tag_pain_description(description):
    # Classify metaphor and dimension
    dimensions, metaphor_types = classify_descriptor_rulebased(description)

    # Get entailments for each metaphor type
    entailments = {met: get_entailments(met) for met in metaphor_types}

    return {
        "text": description,
        "dimensions": dimensions,
        "metaphor_types": metaphor_types,
        "entailments": entailments
    }
