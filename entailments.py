ENTAILMENTS_MAP = {
    "violent_action": [
        "external physical trauma",
        "bodily assault",
        "repeated damage",
        "lack of control",
        "powerlessness"
    ],
    "cutting_tools": [
        "piercing pain",
        "localized sharp injury",
        "invasive action",
        "bodily threat"
    ],
    "internal_machinery": [
        "internal friction",
        "repetitive force",
        "imposed constraint"
    ],
    "constriction_pressure": [
        "pressure from inside or outside",
        "restriction of movement",
        "internal suffocation"
    ],
    "electric_force": [
        "nerve activity",
        "unpredictable spikes",
        "flashes of sensation"
    ],
    "heat": [
        "inflammation",
        "intense irritation",
        "internal temperature dysregulation"
    ],
    "weight_burden": [
        "sense of heaviness",
        "effortful movement",
        "depletion of energy"
    ],
    "birth_labour": [
        "pelvic pressure",
        "wave-like pain",
        "endurance-based agony"
    ],
    "lingering_force": [
        "ongoing discomfort",
        "wearing down",
        "unnoticed but present"
    ],
    "predator": [
        "threat of resurgence",
        "violation",
        "bodily invasion",
        "loss of control",
        "fear",
        "external sentience"
    ],
    "entrapment": [
        "sense of captivity",
        "chronic looping",
        "inability to escape"
    ],
    "transformation_distortion": [
        "dissociation",
        "identity disturbance",
        "pain-induced detachment",
        "loss of coherence"
    ]
}


def get_entailments(metaphor_name):
    """Returns the entailments for a given metaphor type name (in any case format)."""
    return ENTAILMENTS_MAP.get(metaphor_name.lower(), [])
