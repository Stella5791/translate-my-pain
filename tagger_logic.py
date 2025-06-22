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


def tag_pain_description(description, name=None, duration=None):
    text = normalize(description)
    matched = {}
    entailments = {}

    for metaphor_type, data in METAPHOR_TYPES.items():
        for expression in data.get("expressions", []):
            pattern = r'\b' + re.escape(expression.lower()) + r'\b'
            if re.search(pattern, text):
                matched.setdefault(metaphor_type, []).append(expression)
                entailments[metaphor_type] = get_entailments(metaphor_type)
                break

    return {
        "matched_metaphors": matched,
        "entailments": entailments,
        "user_info": {
            "name": name.strip() if name else None,
            "duration": duration.strip() if duration else None
        },
        "input": description.strip()
    }


def generate_doctor_summary(results):
    matched = results.get("matched_metaphors", {})
    input_text = results.get("input", "").lower()

    if not matched:
        return (
            "Your description contains no specific metaphorical patterns that align with known symptom clusters. "
            "However, the language used reflects a complex experience of pain that should be discussed with a healthcare provider for further evaluation."
        )

    summary = ["Here is a clinical summary based on your description:\n"]

    if "constriction_pressure" in matched or "cutting_tools" in matched:
        ovulation_quote = re.search(r"(twisting.*?knife.*?womb)", input_text)
        summary.append("**Ovulation-related pain**")
        if ovulation_quote:
            summary.append(
                f'“{ovulation_quote.group(1)}” — suggests sharp, localized pelvic pain potentially involving ovarian cyst activity, uterine spasms, or visceral hypersensitivity.\n')
        else:
            summary.append(
                "Language involving constriction or stabbing during ovulation may indicate uterine or ovarian origin pain and visceral nerve sensitivity.\n")

    if "heat" in matched:
        period_quote = re.search(r"(fireball.*?(me|inside))", input_text)
        summary.append("**Menstrual pain**")
        if period_quote:
            summary.append(
                f'“{period_quote.group(1)}” — consistent with intense inflammatory flare-ups. Could suggest central sensitization, immune activation, or dysregulated prostaglandin response.\n')
        else:
            summary.append(
                "Burning or explosive language may relate to inflammation, hormonal flares, or neuroimmune disruption during menstruation.\n")

    if "violent_action" in matched or "cutting_tools" in matched:
        sex_quote = re.search(r"(being stabbed)", input_text)
        summary.append("**Dyspareunia (pain with intercourse)**")
        if sex_quote:
            summary.append(
                f'“{sex_quote.group(1)}” — may reflect deep pelvic floor dysfunction, myofascial trigger points, or neuropathic sensitivity.\n')
        else:
            summary.append(
                "Stabbing metaphors during intercourse may reflect trauma, nerve irritation, or muscle dysfunction.\n")

    if "birth_labour" in matched or "cutting_tools" in matched:
        loo_quote = re.search(r"(pushing out.*?sharp)", input_text)
        summary.append("**Defecation-related pain**")
        if loo_quote:
            summary.append(
                f'“{loo_quote.group(1)}” — may indicate endometrial lesions affecting the bowel, rectovaginal septum, or associated nerve pathways.\n')
        else:
            summary.append(
                "Labour-like or cutting metaphors during bowel movements may suggest bowel-involved endometriosis or nerve entrapment.\n")

    if "lingering_force" in matched:
        baseline_quote = re.search(
            r"(dull simmering ache.*?)($|\.|\n)", input_text)
        summary.append("**Chronic baseline pain**")
        if baseline_quote:
            summary.append(
                f'“{baseline_quote.group(1)}” — consistent with low-grade inflammation and emotional fatigue. May be linked to chronic pelvic pain syndrome or persistent somatic distress.\n')
        else:
            summary.append(
                "Dull, ongoing metaphors often signal chronic inflammation, emotional strain, and anticipatory distress.\n")

    summary.append(
        "🩺 *Note*: These metaphor-based interpretations are not diagnostic. They are intended to support communication between patient and provider.\n")
    summary.append("For more information, see the evidence page: /evidence")

    return "\n".join(summary)


def generate_patient_summary(results):
    matched = results.get("matched_metaphors", {})
    input_text = results.get("input", "").lower()
    name = results.get("user_info", {}).get("name", "You")
    duration = results.get("user_info", {}).get("duration")

    if not matched:
        return f"{name}, your pain holds deep meaning, but no specific metaphor patterns were identified this time."

    intro = f"{name}, you're living with pain that holds deep meaning."
    if duration:
        intro += f" You've been experiencing this for {duration.strip()}."
    lines = [intro, ""]

    if "constriction_pressure" in matched or "cutting_tools" in matched:
        lines.append("**During ovulation**: You may feel deep internal pressure or sharp sensations. This could reflect spasms in the uterus, tension in the pelvic floor, or sensitive nerves.")

    if "heat" in matched:
        lines.append("**During menstruation**: Your pain may feel like burning or intense flares. This is often linked to inflammation, hormonal changes, or immune response.")

    if "violent_action" in matched or "cutting_tools" in matched:
        lines.append(
            "**During intercourse**: The pain may be sharp and distressing, possibly due to internal sensitivity, nerve pain, or muscle tension.")

    if "birth_labour" in matched or "cutting_tools" in matched:
        lines.append("**When going to the toilet**: It may feel like pushing something sharp or painful, which might relate to lesions or pressure near the bowel or rectovaginal area.")

    if "lingering_force" in matched:
        lines.append("**At baseline**: Even outside flares, you may live with a dull, simmering ache. This constant background pain can wear you down emotionally and physically.")

    return "\n".join(lines)


def generate_entailment_summary(entailments):
    if not entailments:
        return "No experiential or affective entailments were found."

    summary_lines = [
        "🧠 Clinical interpretations based on metaphor entailments:\n"]

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
