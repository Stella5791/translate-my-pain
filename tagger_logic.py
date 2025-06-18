import re
import json
from entailments import get_entailments
from taxonomy import taxonomy

# --------------------------------------------------------------------------------
# NOTE:
# As of June 2025, researcher notes and rephrasings were integrated directly
# into this file for better performance and portability.
#
# Original external files (now archived in /archive):
# - researcher_notes.json
# - rephrasings.json
#
# This change reduces I/O dependency and simplifies deployment. Restore external
# loading if you later modularize the app or introduce CMS-based editing.
# --------------------------------------------------------------------------------





METAPHOR_TYPES = taxonomy.get("metaphor_types", {})
GRADUATION = taxonomy.get("graduation_modifiers", [])

# Clinical rephrasings for each metaphor type
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

# Research framing summaries
RESEARCHER_FRAMINGS = {
    "constriction_pressure": "This category captures metaphors of tightness, wrapping, or pressure. It is conceptually linked to the idea of bodily containment and internal restriction. Frequently co-occurs with pelvic floor issues.",
    "violent_action": "Includes metaphors of direct assault and external trauma. Often emotionally charged and associated with moments of flare or rupture.",
    "internal_machinery": "Refers to industrial or mechanical metaphors, often indicating dehumanized pain or friction from within. Linked to chronic strain or perceived dysfunction.",
    "cutting_tools": "Captures precise, sharp, and often invasive metaphors. Common in descriptions of acute, localized endometrial or nerve pain.",
    "electric_force": "This type reflects sudden, erratic sensory spikes tied to nerve responses. Common in descriptions of neuropathic or hormonally triggered pain.",
    "heat": "Associated with internal fire, burning, or scalding. Often tied to inflammation, irritation, and hormonal heat dysregulation.",
    "weight_burden": "These metaphors reflect heaviness, burden, and exhaustion. Frequently associated with fatigue, bloating, and emotional overload.",
    "birth_labour": "Taps into reproductive metaphors of childbirth and contractions. Often used by patients with uterine or hormonal patterns of pain.",
    "lingering_force": "Metaphors in this category point to a dull, ever-present discomfort. The language tends to be subdued but communicates chronicity.",
    "predator": "This merged category (formerly monster, lurking_threat, animal_attack) highlights metaphors that personify pain as an external, looming force. Reflects trauma narratives, vigilance, and psychological intrusion.",
    "entrapment": "Captures the logic of the body as a prison or cage. Strong spatial and affective dimensions, particularly among patients with chronic looping pain.",
    "transformation_distortion": "Focuses on metaphors where pain disrupts identity, reality, or bodily integrity. Frequently overlaps with dissociation, trauma, or neurological overwhelm."
}


# --- Tagging Logic --- #
def normalize(text):
    return re.sub(r"[^\w\s']", "", text.lower())


def tag_pain_description(description, name=None, duration=None):
    text = normalize(description)
    matched = {}
    entailments = {}

    for metaphor_type, data in METAPHOR_TYPES.items():
        for expression in data.get("expressions", []):
            if expression in text:
                matched.setdefault(metaphor_type, []).append(expression)
                entailments[metaphor_type] = get_entailments(metaphor_type)
                break

    return {
        "matched_metaphors": matched,
        "entailments": entailments,
        "user_info": {"name": name, "duration": duration}
    }

# --- Summary Builders --- #


def generate_patient_summary(results):
    name = results.get("user_info", {}).get("name")
    duration = results.get("user_info", {}).get("duration")

    intro = f"{name}, you're living with pain that holds deep meaning." if name else "You're living with pain that holds deep meaning."
    if duration:
        intro += f" You've experienced this for {duration}."

    metaphor_types = results.get("matched_metaphors", {}).keys()
    if not metaphor_types:
        return intro + " However, no specific metaphor patterns were identified this time."

    impressions = []
    for mtype in metaphor_types:
        phrase = CLINICAL_REPHRASINGS.get(mtype)
        if phrase:
            impressions.append(phrase)

    return intro + " " + " ".join(impressions)


def generate_doctor_summary(results):
    matched = results.get("matched_metaphors", {})
    if not matched:
        return ("Based on your description, your pain may involve symptoms that suggest underlying inflammation, "
                "nerve sensitivity, or muscular tension. These expressions point to functional disruption and emotional distress, "
                "and should be discussed with a healthcare provider to explore appropriate evaluation and support.")

    output = []
    for metaphor_type in matched:
        phrase = CLINICAL_REPHRASINGS.get(metaphor_type)
        if phrase:
            output.append(f"• {phrase}")

    return "Here is a clinical summary based on the metaphor types in your description:\n\n" + "\n\n".join(output)


def generate_research_summary(results):
    matched = results.get("matched_metaphors", {})
    if not matched:
        return ("The metaphors you've used reflect a rich semantic field of embodied suffering. "
                "This type of language provides valuable insights into how patients conceptualize chronic pain beyond clinical terminology, "
                "supporting a person-centered approach to qualitative health research.")

    output = []
    for metaphor_type in matched:
        notes = RESEARCHER_FRAMINGS.get(metaphor_type)
        if notes:
            output.append(f"• {notes}")

    return "These metaphors contribute to a qualitative understanding of pain communication in context:\n\n" + "\n\n".join(output)


def generate_entailment_summary(entailments):
    if not entailments:
        return "No entailments were found."

    flat_list = [item for sublist in entailments.values() for item in sublist]
    return "These expressions suggest themes like: " + ", ".join(sorted(set(flat_list))) + "."
