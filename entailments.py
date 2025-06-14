ENTAILMENTS_MAP = {
    "Violent Action": [
        "external physical trauma",
        "bodily assault",
        "repeated damage",
        "lack of control",
        "powerlessness"
    ],
    "Cutting Tools": [
        "piercing pain",
        "localized sharp injury",
        "invasive action",
        "bodily threat"
    ],
    "Internal Machinery": [
        "internal friction",
        "repetitive force",
        "imposed constraint"
    ],
    "Constriction Pressure": [
        "pressure from inside or outside",
        "restriction of movement",
        "internal suffocation"
    ],
    "Electric Force": [
        "nerve activity",
        "unpredictable spikes",
        "flashes of sensation"
    ],
    "Heat": [
        "inflammation",
        "intense irritation",
        "internal temperature dysregulation"
    ],
    "Weight Burden": [
        "sense of heaviness",
        "effortful movement",
        "depletion of energy"
    ],
    "Birth Labour": [
        "pelvic pressure",
        "wave-like pain",
        "endurance-based agony"
    ],
    "Background Pain": [
        "ongoing discomfort",
        "wearing down",
        "unnoticed but present"
    ],
    "Predator": [
        "threat of resurgence",
        "violation",
        "bodily invasion",
        "loss of control",
        "fear",
        "external sentience"
    ],
    "Entrapment": [
        "sense of captivity",
        "chronic looping",
        "inability to escape"
    ],
    "Transformation Distortion": [
        "dissociation",
        "identity disturbance",
        "pain-induced detachment",
        "loss of coherence"
    ]
}


def get_entailments(metaphor_name):
    return ENTAILMENTS_MAP.get(metaphor_name, [])
