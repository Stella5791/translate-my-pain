import re
from entailments import get_entailments
from taxonomy import taxonomy

# Load taxonomy components
METAPHOR_TYPES = taxonomy.get("metaphor_types", {})
GRADUATION = taxonomy.get("graduation_modifiers", [])
TRIGGERS = taxonomy.get("triggers", [])
LIFE_IMPACT = taxonomy.get("life_impact_clues", [])

# Clinical rephrasings
CLINICAL_REPHRASINGS = {
    "violent_action": "Your pain may feel like a violent intrusion on your body, consistent with severe, traumatic episodes.",
    "cutting_tools": "The pain resembles being cut or pierced, possibly indicating sharp, localized discomfort.",
    "internal_machinery": "It feels like something mechanical is grinding or compressing your insides — a harsh, internal disruption.",
    "constriction_pressure": "You may feel intense internal pressure or tightening, as if your body is being squeezed or strangled.",
    "electric_force": "It’s like sudden, sharp shocks or buzzing, which could reflect nerve sensitivity or episodic flare-ups.",
    "weight_burden": "Your pain feels heavy and draining, as if you're carrying something too weighty for your body to bear.",
    "heat": "There’s a burning or searing quality to your pain, often associated with inflammation or heat deep inside.",
    "birth_labour": "The pain mimics labour or birthing sensations — cyclical, intense, and radiating from deep within the pelvis.",
    "lingering_force": "Even when not at its peak, the pain simmers beneath the surface, never fully letting go.",
    "predator": "It feels like something foreign is lurking inside you — invasive, unpredictable, and threatening.",
    "entrapment": "You may feel trapped inside your body, caught in a loop of pain that limits your freedom.",
    "transformation_distortion": "The pain affects how you see yourself — altering your sense of identity or making you feel detached from your body.",
    "literal": "You’re using direct physical terms to describe your pain. This language is clear and still very meaningful."
}


def normalize(text):
    return re.sub(r"[^\w\s']", "", text.lower())


# --- Context detection helpers ---
_CONTEXTS = {
    "menstruation": [
        r"\b(during|on|with)\s+(my\s+)?period\b",
        r"\bmenstruat(?:e|ion|ing|ory)\b",
        r"\b(menses|bleeding|time of the month)\b",
    ],
    "ovulation": [
        r"\bovulat(?:e|ion|ing|ory)\b",
        r"\bmid\s*cycle\b",
        r"\b(fertile|egg release)\b",
    ],
    "intercourse": [
        r"\b(during|with)\s+(sex|intercourse|penetration)\b",
        r"\bpenetration\b",
    ],
    "defecation": [
        r"\b(during|when|while)\s+(poo|poop|defecat(?:e|ion)|bowel (?:movement|movements)|going to the toilet)\b",
        r"\bpassing (?:stool|bowel movements?)\b",
    ],
    "baseline": [
        r"\b(rest of the month|outside (?:of )?(?:flares|periods?)|most days|all the time|baseline)\b",
        r"\bbetween (?:periods|flares)\b",
    ],
}


def _find_spans(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    spans = {k: [] for k in _CONTEXTS.keys()}

    for sent in sentences:
        low = sent.lower()
        for ctx, pats in _CONTEXTS.items():
            if any(re.search(p, low) for p in pats):
                spans[ctx].append(sent.strip())

    if not any(spans.values()):
        spans["baseline"] = [text.strip()]

    return spans


def _match_metaphors_in(text_norm):
    found = set()
    for metaphor_type, data in METAPHOR_TYPES.items():
        for expression in data.get("expressions", []):
            pattern = re.escape(expression.lower())
            if re.search(pattern, text_norm):
                found.add(metaphor_type)
                break
    return found


def tag_pain_description(description, name=None, duration=None):
    raw = description.strip()
    spans = _find_spans(raw)
    matched_by_context = {}
    global_matched = set()
    entailments = {}

    for ctx, chunks in spans.items():
        ctx_found = set()
        for chunk in chunks:
            ctx_found |= _match_metaphors_in(normalize(chunk))
        if ctx_found:
            matched_by_context[ctx] = sorted(ctx_found)
            global_matched |= ctx_found

    for mtype in sorted(global_matched):
        entailments[mtype] = get_entailments(mtype)

    return {
        "matched_metaphors": {m: True for m in sorted(global_matched)},
        "matched_by_context": matched_by_context,
        "entailments": entailments,
        "user_info": {
            "name": name.strip() if isinstance(name, str) and name.strip() else None,
            "duration": duration.strip() if isinstance(duration, str) and duration.strip() else None
        },
        "input": raw,
    }


def generate_patient_summary(results):
    matched_global = results.get("matched_metaphors", {})
    matched_ctx = results.get("matched_by_context", {})
    input_text = (results.get("input") or "").lower()
    name = (results.get("user_info", {}).get("name")) or "You"
    duration = results.get("user_info", {}).get("duration")

    if not matched_global:
        return f"{name}, you're living with pain that holds deep meaning. No specific metaphor patterns were identified this time."

    intro = f"{name}, you're living with pain that holds deep meaning."
    if duration:
        intro += f" You've been experiencing this for {duration.strip()}."
    lines = [intro, ""]

    if "ovulation" in matched_ctx:
        if any(m in matched_ctx["ovulation"] for m in ("constriction_pressure", "cutting_tools", "violent_action", "electric_force")):
            lines.append(
                "**During ovulation**: You may feel deep pressure or sharp, stabbing sensations—often tied to uterine/ovarian spasms or nerve sensitivity.")

    if "menstruation" in matched_ctx:
        if "heat" in matched_ctx["menstruation"] or "birth_labour" in matched_ctx["menstruation"]:
            lines.append(
                "**During menstruation**: The pain can burn or surge like flares, consistent with inflammatory or neuroimmune drivers.")

    if "intercourse" in matched_ctx:
        if any(m in matched_ctx["intercourse"] for m in ("violent_action", "cutting_tools", "constriction_pressure")):
            lines.append(
                "**During intercourse**: Sharp or intrusive sensations may reflect pelvic floor tension or localized nerve irritation.")

    if "defecation" in matched_ctx:
        if any(m in matched_ctx["defecation"] for m in ("birth_labour", "cutting_tools", "constriction_pressure")):
            lines.append(
                "**When going to the toilet**: Labour-like pressure or cutting sensations can signal bowel involvement or nearby nerve entrapment.")

    if "baseline" in matched_ctx:
        if any(m in matched_ctx["baseline"] for m in ("lingering_force", "predator", "weight_burden")):
            lines.append(
                "**The rest of the month**: A constant, lurking or heavy ache can drain energy and heighten anticipatory stress.")

    for ctx_label, human in [
        ("ovulation", "**During ovulation**"),
        ("menstruation", "**During menstruation**"),
        ("intercourse", "**During intercourse**"),
        ("defecation", "**When going to the toilet**"),
        ("baseline", "**The rest of the month**"),
    ]:
        if ctx_label in results.get("matched_by_context", {}) or re.search("|".join(_CONTEXTS[ctx_label]), input_text):
            if not any(line.startswith(human) for line in lines):
                lines.append(
                    f"{human}: You mentioned this, and it matters—even if no specific patterns were detected here today.")

    return "
".join(lines)

def generate_doctor_summary(results):
    matched_global = results.get("matched_metaphors", {})
    matched_ctx = results.get("matched_by_context", {})
    if not matched_global:
        return ("Your description contains no specific metaphorical patterns that align with known symptom clusters. "
                "However, the language used reflects a complex experience of pain that should be discussed with a healthcare provider for further evaluation.")

    out = ["Here is a clinical summary based on your description:
"]

    if "ovulation" in matched_ctx:
        if any(m in matched_ctx["ovulation"] for m in ("constriction_pressure", "cutting_tools", "violent_action", "electric_force")):
            out.append("**Ovulation-related pain**")
            out.append("Language indicating constriction/stabbing around ovulation suggests uterine/ovarian origin and visceral nerve sensitivity.
")

    if "menstruation" in matched_ctx:
        if "heat" in matched_ctx["menstruation"] or "birth_labour" in matched_ctx["menstruation"]:
            out.append("**Menstrual pain**")
            out.append("Burning/flaring language aligns with inflammatory flares or neuroimmune dysregulation during menses.
")

    if "intercourse" in matched_ctx:
        if any(m in matched_ctx["intercourse"] for m in ("violent_action", "cutting_tools", "constriction_pressure")):
            out.append("**Dyspareunia (pain with intercourse)**")
            out.append("Intrusive/cutting metaphors during intercourse may reflect pelvic floor dysfunction, trauma sequelae, or localized neuropathic irritation.
")

    if "defecation" in matched_ctx:
        if any(m in matched_ctx["defecation"] for m in ("birth_labour", "cutting_tools", "constriction_pressure")):
            out.append("**Defecation-related pain**")
            out.append("Labour-like/knife-like metaphors with bowel movements may indicate bowel involvement or nerve entrapment.
")

    if "baseline" in matched_ctx:
        if any(m in matched_ctx["baseline"] for m in ("lingering_force", "predator", "weight_burden")):
            out.append("**Chronic baseline pain**")
            out.append("Persistent, lurking/heavy metaphors point to chronic inflammation with anticipatory distress.
")

    out.append("🩺 *Note*: These metaphor-based interpretations are not diagnostic. They are intended to support communication between patient and provider.
")
    out.append("For more information, see the evidence page: /evidence")
    return "
".join(out)


def generate_entailment_summary(entailments):
    if not entailments:
        return "No experiential or affective entailments were found."

    summary_lines = [
        " Clinical interpretations based on metaphor entailments:\n"]

    for metaphor_type, values in entailments.items():
        experiential = values.get("experiential", [])
        affective = values.get("affective", [])

        if experiential:
            summary_lines.append(
                f"• **{metaphor_type}** – Experiential entailments: {', '.join(experiential)}")
        if affective:
            summary_lines.append(
                f"  – Affective entailments: {', '.join(affective)}")

    summary_lines.append(
        "\nThese interpretations can support shared understanding between patients and clinicians.")
    return "\n".join(summary_lines)
