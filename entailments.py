ENTAILMENTS_MAP = {
    "violent_action": {
        "entailments": [
            "external physical trauma",
            "bodily assault",
            "repeated damage",
            "lack of control",
            "powerlessness"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "cutting_tools": {
        "entailments": [
            "piercing pain",
            "localized sharp injury",
            "invasive action",
            "bodily threat"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "internal_machinery": {
        "entailments": [
            "internal friction",
            "repetitive force",
            "imposed constraint"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "constriction_pressure": {
        "entailments": [
            "pressure from inside or outside",
            "restriction of movement",
            "internal suffocation"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "electric_force": {
        "entailments": [
            "nerve activity",
            "unpredictable spikes",
            "flashes of sensation"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "heat": {
        "entailments": [
            "inflammation",
            "intense irritation",
            "internal temperature dysregulation"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "weight_burden": {
        "entailments": [
            "sense of heaviness",
            "effortful movement",
            "depletion of energy"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "birth_labour": {
        "entailments": [
            "pelvic pressure",
            "wave-like pain",
            "endurance-based agony"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "lingering_force": {
        "entailments": [
            "ongoing discomfort",
            "wearing down",
            "unnoticed but present"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "predator": {
        "entailments": [
            "threat of resurgence",
            "violation",
            "bodily invasion",
            "loss of control",
            "fear",
            "external sentience"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "entrapment": {
        "entailments": [
            "sense of captivity",
            "chronic looping",
            "inability to escape"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    },
    "transformation_distortion": {
        "entailments": [
            "dissociation",
            "identity disturbance",
            "pain-induced detachment",
            "loss of coherence"
        ],
        "literature_source": "Bullo (2024), 'Parallel Words', BJHP"
    }
}


def get_entailments(metaphor_name):
    """Returns the list of entailments for a given metaphor type."""
    return ENTAILMENTS_MAP.get(metaphor_name.lower(), {}).get("entailments", [])
