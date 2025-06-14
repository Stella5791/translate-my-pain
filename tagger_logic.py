import json
import re
import logging
from entailments import get_entailments

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load taxonomy and related data
with open("taxonomy.json") as f:
    taxonomy = json.load(f)

with open("rephrasings.json") as f:
    rephrasings = json.load(f)

with open("researcher_notes.json") as f:
    researcher_notes = json.load(f)

# Normalize and clean expressions at load time
metaphor_types = taxonomy.get("metaphor_types", {})
for cat in metaphor_types.values():
    cat["expressions"] = [
        re.sub(r"[^\w\s']", "", expr.lower()) for expr in cat.get("expressions", [])
    ]
    cat["dimensions"] = [dim.lower() for dim in cat.get("dimensions", [])]

GRADUATION = [g.lower() for g in taxonomy.get("graduation_modifiers", [])]
TRIGGERS = [t.lower() for t in taxonomy.get("triggers", [])]
IMPACT_CLUES = [c.lower() for c in taxonomy.get("life_impact_clues", [])]
DELIMITERS = r"[^\w']+"


def normalize_text(text):
    return re.sub(r"[^\w\s']", "", text.lower())


def generate_ngrams(tokens, max_n=4):
    ngram_list = []
    for n in range(1, max_n + 1):
        ngram_list.extend([
            " ".join(gram)
            for gram in zip(*[tokens[i:] for i in range(n)])
        ])
    return ngram_list


def build_plain_summary(dimensions, triggers, graduation, impact):
    if not (dimensions or triggers or graduation or impact):
        return "Your description didn't match known symptom patterns, but it still matters."

    parts = []
    if graduation:
        parts.append(f"You described the pain as {', '.join(graduation)}.")
    if dimensions:
        parts.append(
            f"It seems to involve aspects like {', '.join(dimensions)}.")
    if triggers:
        parts.append(f"It is often triggered by {', '.join(triggers)}.")
    if impact:
        parts.append(
            f"This pain seems to affect daily life: {', '.join(impact)}.")

    return " ".join(parts)


def tag_pain_description(text, name=None, duration=None):
    logger.info("User input: %s", text)

    normalized_text = normalize_text(text)
    tokens = normalized_text.split()
    ngram_set = set(generate_ngrams(tokens))

    detected = {
        "metaphors": set(),
        "dimensions": set(),
        "triggers": set(),
        "graduation": set()
    }

    matches = {}
    for category, items in metaphor_types.items():
        match_list = []
        for expr in items.get("expressions", []):
            if expr in ngram_set:
                detected["metaphors"].add(category)
                match_list.append(expr)
        if match_list:
            matches[category] = match_list

    for category, items in metaphor_types.items():
        for dim in items.get("dimensions", []):
            if dim in normalized_text:
                detected["dimensions"].add(dim)

    for trigger in TRIGGERS:
        if trigger in normalized_text:
            detected["triggers"].add(trigger)

    for grad in GRADUATION:
        if grad in normalized_text:
            detected["graduation"].add(grad)

    impact_context = [clue for clue in IMPACT_CLUES if clue in normalized_text]

    entailments = {
        m: get_entailments(m.title().replace("_", " "))
        for m in detected["metaphors"]
    }

    clinical_rephrasings = {
        m: rephrasings[m] for m in detected["metaphors"] if m in rephrasings
    }

    research = {
        m: researcher_notes[m] for m in detected["metaphors"] if m in researcher_notes
    }

    plain_summary = build_plain_summary(
        list(detected["dimensions"]),
        list(detected["triggers"]),
        list(detected["graduation"]),
        impact_context
    )

    dominant_metaphor = max(
        matches.items(), key=lambda x: len(x[1]), default=(None, []))[0]

    return {
        "input": text,
        "metaphors": list(detected["metaphors"]),
        "dominant_metaphor": dominant_metaphor,
        "dimensions": list(detected["dimensions"]),
        "triggers": list(detected["triggers"]),
        "graduation": list(detected["graduation"]),
        "impact_context": impact_context,
        "matches": matches,
        "entailments": entailments,
        "clinical_rephrasings": clinical_rephrasings,
        "research": research,
        "plain_summary": plain_summary,
        "user_info": {
            "name": name,
            "duration": duration
        }
    }


def generate_patient_summary(results):
    name = results.get("user_info", {}).get("name", "You")
    duration = results.get("user_info", {}).get("duration")
    metaphors = results.get("clinical_rephrasings", {})
    entailments = results.get("entailments", {})
    triggers = results.get("triggers", [])
    impact = results.get("impact_context", [])

    lines = []

    if name != "You":
        intro = f"{name}, based on the language you used, here's a summary of how your pain may feel:"
    else:
        intro = "Based on the language you used, here's a summary of how your pain may feel:"

    if duration:
        intro += f" You've been experiencing this pain for {duration}."

    lines.append(intro)

    if triggers:
        trigger_text = ", ".join(triggers)
        lines.append(f"It tends to occur or worsen during: {trigger_text}.")

    for category, details in metaphors.items():
        feeling = details.get("patient_friendly")
        entailed = entailments.get(category, [])
        entail_str = ", ".join(entailed) if entailed else ""
        if feeling:
            lines.append(
                f"{feeling} This kind of pain may involve: {entail_str}.")

    if impact:
        impact_str = ", ".join(impact)
        lines.append(
            f"This pain seems to affect your daily life significantly: {impact_str}.")

    return " ".join(lines)


def generate_doctor_summary(results):
    metaphors = results.get("clinical_rephrasings", {})
    entailments = results.get("entailments", {})
    triggers = results.get("triggers", [])
    impact = results.get("impact_context", [])

    lines = ["This patient's description includes metaphorical language that suggests specific underlying mechanisms."]

    if triggers:
        lines.append("Reported triggers include: " + ", ".join(triggers) + ".")

    for category, data in metaphors.items():
        mech = data.get("likely_mechanism", "")
        terms = ", ".join(data.get("clinical_terms", [])) if isinstance(
            data.get("clinical_terms"), list) else data.get("clinical_terms", "")
        entail_str = ", ".join(entailments.get(category, []))
        lines.append(
            f"• {category.replace('_', ' ').title()}: {mech}. Clinical terms: {terms}. Indicative features include: {entail_str}."
        )

    if impact:
        lines.append("Reported impact on quality of life: " +
                     ", ".join(impact) + ".")

    return " ".join(lines)


def generate_research_summary(results):
    metaphors = results.get("research", {})
    entailments = results.get("entailments", {})

    lines = ["This entry includes the following metaphor categories with interpretive and theoretical implications:"]

    for category, note in metaphors.items():
        entail_str = ", ".join(entailments.get(category, []))
        lines.append(
            f"• {category.replace('_', ' ').title()}: {note} Entailments: {entail_str}.")

    return " ".join(lines)
