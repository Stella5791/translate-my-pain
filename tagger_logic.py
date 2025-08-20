# tagger_logic.py — taxonomy-aligned metaphor tagger with patient/doctor narratives
# Uses Bullo's research-derived taxonomy.

import re
from typing import Dict, List, Set
from taxonomy import taxonomy
# -> {"experiential":[...], "affective":[...]}
from entailments import get_entailments

# -----------------------
# Expose taxonomy parts for downstream / future UI
# -----------------------
METAPHOR_TYPES: Dict = taxonomy.get("metaphor_types", {})
GRADUATION: List[str] = taxonomy.get("graduation_modifiers", [])
TRIGGERS: List[str] = taxonomy.get("triggers", [])
LIFE_IMPACT: List[str] = taxonomy.get("life_impact_clues", [])

# -----------------------
# Patient-facing rephrasings (original set)
# -----------------------
CLINICAL_REPHRASINGS: Dict[str, str] = {
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

# -----------------------
# Normalization helpers
# -----------------------


def _normalize(text: str) -> str:
    """Lowercase and strip punctuation except spaces and apostrophes."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    return re.sub(r"[^\w\s']", " ", text.lower()).strip()


def _irregular_word_variants(word: str) -> List[str]:
    """
    Return common irregular singular/plural variants for a single word.
    Covers knife→knives and generic f/fe→ves patterns without overgeneration.
    """
    w = (word or "").strip().lower()
    alts = {w}

    # Specific map for safety; extend as you encounter more irregulars.
    specific = {
        "knife": {"knives"},
        "leaf": {"leaves"},
        "wolf": {"wolves"},
        "calf": {"calves"},
        "shelf": {"shelves"},
        "loaf": {"loaves"},
        "life": {"lives"},
        "wife": {"wives"},
    }
    if w in specific:
        alts |= specific[w]

    # Generic f/fe → ves (only if it looks like a real base form)
    if w.endswith("fe") and len(w) > 2:
        alts.add(w[:-2] + "ves")
    if w.endswith("f") and len(w) > 1:
        alts.add(w[:-1] + "ves")

    return sorted(alts)


def _compile_expression(expr: str) -> re.Pattern:
    r"""
    Build a forgiving regex from a taxonomy expression:
      - multiword → collapse internal whitespace to \s+
      - single word → match root + (ing|ed|es|s) with doubled-consonant safety
      - include irregular plural/singular alternations (knife|knives, etc.)
    """
    expr = (expr or "").strip().lower()
    if not expr:
        return re.compile(r"(?!x)x")  # never matches

    # Multiword expression: keep exact words but allow flexible spacing
    if " " in expr:
        parts = [re.escape(p) for p in expr.split()]
        pattern = r"\b" + r"\s+".join(parts) + r"\b"
        return re.compile(pattern, re.I)

    # Single-word expression: generate variants
    word = expr

    # Irregular alternations like knife|knives
    irregulars = set(_irregular_word_variants(word))

    # Root variants for regular suffixes
    root = re.sub(r"(?:ing|ed|es|s)$", "", word)
    variants = {word, root} | irregulars

    # handle doubled final consonant after stripping (e.g., 'stabbed' -> 'stabb' -> 'stab')
    if len(root) >= 2 and root[-1] == root[-2]:
        variants.add(root[:-1])

    # Build alternation; for forms ending in 'ves' do NOT add extra suffixes
    alts = []
    for v in variants:
        if v.endswith("ves"):
            alts.append(re.escape(v))  # exact plural
        elif len(v) >= 3:
            alts.append(re.escape(v) + r"(?:ing|ed|es|s)?")
        else:
            alts.append(re.escape(v))
    alts = sorted(set(alts), key=len, reverse=True)

    pattern = r"\b(?:%s)\b" % "|".join(alts)
    return re.compile(pattern, re.I)


# Precompile patterns from taxonomy once
_COMPILED: Dict[str, List[re.Pattern]] = {
    mtype: [_compile_expression(e) for e in data.get("expressions", [])]
    for mtype, data in METAPHOR_TYPES.items()
}


def _match_metaphors_in(text_norm: str) -> Set[str]:
    """Return a set of taxonomy categories found in normalized text."""
    found: Set[str] = set()
    for mtype, pats in _COMPILED.items():
        for pat in pats:
            if pat.search(text_norm):
                found.add(mtype)
                break
    return found

# ---------------------------------------
# Debias: predator anticipation vs assault
# ---------------------------------------


def _debias_predator_vs_violent(chunk_text: str, cats: Set[str]) -> Set[str]:
    """
    If language is about anticipation of attack alongside predator imagery,
    treat it as 'predator' rather than 'violent_action'.
    Example: "waiting for the lurking animal to attack me"
    """
    if "violent_action" in cats and "predator" in cats:
        low = (chunk_text or "").lower()
        anticip = re.search(r"\b(waiting|about to|ready to|going to)\s+attack\b", low) or \
            re.search(r"\battack me\b", low)
        if anticip and any(tok in low for tok in ("lurking", "monster", "beast", "predator")):
            cats = set(cats)
            cats.discard("violent_action")
    return cats


# -----------------------
# Context detection (matches earlier app)
# -----------------------
_CONTEXTS = {
    "menstruation": [
        r"\b(during|on|with)\s+(my\s+)?period\b",
        r"\bmenstruat(?:e|ion|ing|ory)\b",
        r"\b(menses|bleeding|time of the month)\b",
    ],
    "ovulation": [
        r"\bovulat(?:e|ion|ing|ory)\b",
        r"\bmid\s*cycle\b",
        r"\b(fertile|egg\s*release)\b",
    ],
    "intercourse": [
        r"\b(during|with)\s+(sex|intercourse|penetration)\b",
        r"\bpenetration\b",
    ],
    "defecation": [
        r"\b(during|when|while)\s+(poo|poop|defecat(?:e|ion)|bowel (?:movement|movements)|going to the toilet)\b",
        r"\bgoing to the toilet\b",
        r"\bpassing (?:stool|bowel movements?)\b",
    ],
    "baseline": [
        r"\b(rest of the month|outside (?:of )?(?:flares|periods?)|most days|all the time|baseline)\b",
        r"\bbetween (?:periods|flares)\b",
    ],
}


def _find_spans(text: str):
    """
    Light sentence segmentation; if multiple contexts appear in one sentence,
    that sentence is attached to each mentioned context.
    """
    sentences = re.split(r'(?<=[.!?;])\s+', (text or "").strip())
    if not sentences:
        sentences = [(text or "").strip()]

    spans = {k: [] for k in _CONTEXTS.keys()}

    for sent in sentences:
        low = sent.lower()
        for ctx, pats in _CONTEXTS.items():
            if any(re.search(p, low) for p in pats):
                spans[ctx].append(sent.strip())

    # If nothing matched any context, treat whole text as baseline
    if not any(spans.values()):
        spans["baseline"] = [(text or "").strip()]

    return spans

# -----------------------
# Extra: detect triggers & life-impact mentions (light, non-breaking)
# -----------------------


def _detect_list_mentions(text_norm: str, items: List[str]) -> List[str]:
    hits = []
    for item in items:
        token = (item or "").strip().lower()
        if not token:
            continue
        if token in text_norm:
            hits.append(item)
    return sorted(set(hits))

# -----------------------
# Sensory vs Emotional cues
# -----------------------


def _summarize_signals(entailments: dict) -> str:
    """
    Build a compact 'Sensory vs Emotional' summary from entailments.
    Ensures affective items (fear, threat, loss of control, violation, invasion, etc.)
    are shown under Emotional cues, while physical terms (heat, inflammation, sharp, pressure, shock, etc.)
    go under Sensory cues.
    """
    # Flatten whatever shape we get: mapping -> lists
    items = []
    if isinstance(entailments, dict):
        for vals in entailments.values():
            if isinstance(vals, dict):
                items.extend(vals.get("experiential", []))
                items.extend(vals.get("affective", []))
            elif isinstance(vals, list):
                items.extend(vals)

    # Keyword heuristics to bin phrases
    AFFECTIVE_HINTS = (
        "fear", "anxiety", "threat", "loss of control", "powerless", "powerlessness",
        "hopeless", "worry", "violation", "invasion", "anticipat", "sentience",
        "identity", "dissociation", "detachment", "stress", "hypervigilance"
    )
    SENSORY_HINTS = (
        "inflammation", "irritation", "temperature", "heat", "hot", "burn", "searing",
        "piercing", "sharp", "localized", "pressure", "tight", "tightening", "constriction",
        "crush", "heavy", "heaviness", "shock", "zapping", "tingling", "electr", "spasm",
        "nerve", "neuropath", "tearing", "pulling", "weight", "drag"
    )

    sens, emo = set(), set()
    for p in items:
        s = str(p).strip()
        if not s:
            continue
        low = s.lower()
        is_aff = any(k in low for k in AFFECTIVE_HINTS)
        is_sens = any(k in low for k in SENSORY_HINTS)

        if is_aff and not is_sens:
            emo.add(s)
        elif is_sens and not is_aff:
            sens.add(s)
        elif is_aff and is_sens:
            # If ambiguous, prefer Emotional to avoid minimizing affective content
            emo.add(s)
        else:
            # Unclassified -> omit to keep the section tight
            continue

    def _fmt(seq, label):
        if not seq:
            return ""
        vals = sorted(seq)
        if len(vals) > 8:
            vals = vals[:7] + ["…"]
        return f"**{label}**: " + ", ".join(vals) + "."

    parts = []
    sc = _fmt(sens, "Sensory cues")
    ec = _fmt(emo, "Emotional cues")
    if sc:
        parts.append(sc)
    if ec:
        parts.append(ec)
    return "\n".join(parts)

# -----------------------
# Public API (consumed by app.py)
# -----------------------


def tag_pain_description(description, name=None, duration=None):
    """
    Returns:
      - matched_metaphors: {category: True}
      - matched_by_context: {context: [categories]}
      - entailments: {category: {"experiential":[...], "affective":[...]}}
      - user_info: {name, duration}
      - input: original text
      - extras: {triggers_detected: [...], life_impact_detected: [...]}
    """
    raw = (description or "").strip()
    norm = _normalize(raw)
    spans = _find_spans(raw)

    matched_by_context: Dict[str, List[str]] = {}
    global_matched: Set[str] = set()
    entailments: Dict[str, Dict[str, List[str]]] = {}

    for ctx, chunks in spans.items():
        ctx_found: Set[str] = set()
        for chunk in chunks:
            cats = _match_metaphors_in(_normalize(chunk))
            cats = _debias_predator_vs_violent(chunk, cats)
            ctx_found |= cats
        if ctx_found:
            matched_by_context[ctx] = sorted(ctx_found)
            global_matched |= ctx_found

    for mtype in sorted(global_matched):
        entailments[mtype] = get_entailments(mtype)

    triggers_detected = _detect_list_mentions(
        norm, TRIGGERS) if TRIGGERS else []
    life_impact_detected = _detect_list_mentions(
        norm, LIFE_IMPACT) if LIFE_IMPACT else []

    return {
        "matched_metaphors": {m: True for m in sorted(global_matched)},
        "matched_by_context": matched_by_context,
        "entailments": entailments,
        "user_info": {
            "name": name.strip() if isinstance(name, str) and name.strip() else None,
            "duration": duration.strip() if isinstance(duration, str) and duration.strip() else None
        },
        "input": raw,
        "extras": {
            "triggers_detected": triggers_detected,
            "life_impact_detected": life_impact_detected
        }
    }


def generate_patient_summary(results) -> str:
    """
    Patient-facing rephrasing with gentle explanations per context.
    Uses CLINICAL_REPHRASINGS where available. (No Sensory/Emotional block here.)
    """
    if not isinstance(results, dict):
        return "You're living with pain that holds deep meaning."

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

    order = ["menstruation", "ovulation",
             "intercourse", "defecation", "baseline"]
    labels = {
        "menstruation": "**During menstruation**",
        "ovulation": "**During ovulation**",
        "intercourse": "**During intercourse**",
        "defecation": "**When going to the toilet**",
        "baseline": "**The rest of the month**",
    }

    for ctx in order:
        cats = matched_ctx.get(ctx, [])
        if not cats:
            # Acknowledge mentioned contexts even if no metaphors detected
            for pat in _CONTEXTS.get(ctx, []):
                if re.search(pat, input_text):
                    lines.append(
                        f"{labels[ctx]}: You mentioned this, and it matters—even if no specific patterns were detected here today."
                    )
                    break
            continue

        # Build a concise, readable sentence using a gentle priority
        PRIORITY = [
            "heat",                 # burning/searing
            "cutting_tools",        # sharp/piercing
            "constriction_pressure",
            "electric_force",
            "weight_burden",
            "birth_labour",
            "internal_machinery",
            "lingering_force",
            "predator",
            "entrapment",
            "transformation_distortion",
            "violent_action",       # last (heaviest wording)
        ]

        chosen = None
        for key in PRIORITY:
            if key in cats and key in CLINICAL_REPHRASINGS:
                chosen = CLINICAL_REPHRASINGS[key]
                break

        if not chosen:
            # Fallback if no rephrasing exists
            human = ", ".join(c.replace("_", " ") for c in cats[:3])
            chosen = f"You describe {human} sensations."

        lines.append(f"{labels[ctx]}: {chosen}")

    return "\n".join(lines)


def generate_doctor_summary(results) -> str:
    """
    Clinician-facing narrative based on taxonomy categories and contexts.
    Includes Sensory/Emotional cues aggregated from entailments.
    """
    if not isinstance(results, dict):
        return "Here is a clinical summary based on your description:\n\n🩺 *Note*: These metaphor-based interpretations are not diagnostic."

    matched_global = results.get("matched_metaphors", {})
    matched_ctx = results.get("matched_by_context", {})

    if not matched_global:
        return (
            "Your description contains no specific metaphorical patterns that align with known symptom clusters. "
            "However, the language used reflects a complex experience of pain that should be discussed with a healthcare provider for further evaluation."
        )

    out = ["Here is a clinical summary based on your description:\n"]

    if "ovulation" in matched_ctx:
        if any(m in matched_ctx["ovulation"] for m in ("constriction_pressure", "cutting_tools", "violent_action", "electric_force")):
            out.append("**Ovulation-related pain**")
            out.append(
                "Language indicating constriction/stabbing around ovulation suggests uterine/ovarian origin and visceral nerve sensitivity.\n")

    if "menstruation" in matched_ctx:
        if "heat" in matched_ctx["menstruation"] or "birth_labour" in matched_ctx["menstruation"]:
            out.append("**Menstrual pain**")
            out.append(
                "Burning/flaring language aligns with inflammatory flares or neuroimmune dysregulation during menses.\n")

    if "intercourse" in matched_ctx:
        if any(m in matched_ctx["intercourse"] for m in ("violent_action", "cutting_tools", "constriction_pressure")):
            out.append("**Dyspareunia (pain with intercourse)**")
            out.append("Intrusive/cutting metaphors during intercourse may reflect pelvic floor dysfunction, trauma sequelae, or localized neuropathic irritation.\n")

    if "defecation" in matched_ctx:
        if any(m in matched_ctx["defecation"] for m in ("birth_labour", "cutting_tools", "constriction_pressure", "heat", "violent_action")):
            out.append("**Defecation-related pain**")
            out.append("Labour-like/knife-like or burning metaphors with bowel movements may indicate bowel involvement, inflammatory irritation, or nearby nerve entrapment.\n")

    if "baseline" in matched_ctx:
        if any(m in matched_ctx["baseline"] for m in ("lingering_force", "predator", "weight_burden")):
            out.append("**Chronic baseline pain**")
            out.append(
                "Persistent, lurking/heavy metaphors point to chronic inflammation with anticipatory distress.\n")

    # Add Sensory/Emotional cues summary
    signals = _summarize_signals(results.get("entailments", {}))
    if signals:
        out.extend(
            ["", "**Interpretive signals** (from metaphor entailments):", signals, ""])

    out.append("🩺 *Note*: These metaphor-based interpretations are not diagnostic. They are intended to support communication between patient and provider.\n")
    out.append("For more information, see the evidence page: /evidence")

    return "\n".join(out)


def generate_entailment_summary(obj) -> str:
    """
    Accepts either:
      - an entailments mapping dict: {category: {"experiential":[...], "affective":[...]}}
      - a full results dict containing 'entailments'
    Returns a bullet-point summary.
    """
    mapping = {}
    if isinstance(obj, dict):
        # mapping already
        if obj and all(isinstance(k, str) for k in obj.keys()) and ("experiential" in next(iter(obj.values()), {}) or "affective" in next(iter(obj.values()), {})):
            mapping = obj
        # or whole results
        elif "entailments" in obj:
            mapping = obj.get("entailments", {})

    if not mapping:
        return "No experiential or affective entailments were found."

    lines = [" Clinical interpretations based on metaphor entailments:\n"]
    for mtype, vals in mapping.items():
        exp = vals.get("experiential", [])
        aff = vals.get("affective", [])
        if exp:
            lines.append(
                f"• **{mtype}** – Experiential entailments: {', '.join(exp)}")
        if aff:
            lines.append(f"  – Affective entailments: {', '.join(aff)}")

    lines.append(
        "\nThese interpretations can support shared understanding between patients and clinicians.")
    return "\n".join(lines)

# Backwards-compatibility alias some callers might use


def generate_doctor_narrative(results) -> str:
    return generate_doctor_summary(results)
