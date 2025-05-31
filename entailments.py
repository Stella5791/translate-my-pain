entailments_map = {
    "Burning": {
        "experiential": ["heat", "stinging", "surface-level or deep tissue"],
        "affective": ["intensity", "agitation", "alarm"]
    },
    "Pressure": {
        "experiential": ["tightness", "weight", "constriction"],
        "affective": ["oppression", "stress", "burden"]
    },
    "Monster": {
        "experiential": ["invasion", "presence", "agency"],
        "affective": ["fear", "helplessness", "violation"]
    },
    "Knife": {
        "experiential": ["cutting", "sharpness", "sudden onset"],
        "affective": ["shock", "danger", "violence"]
    },
    # Add more categories as needed
}


def get_entailments(category):
    return entailments_map.get(category, {
        "experiential": [],
        "affective": []
    })
