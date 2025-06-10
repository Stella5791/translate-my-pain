from flask import Flask, render_template, request
import re
import json
import logging

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load taxonomy
with open('taxonomy.json') as f:
    taxonomy = json.load(f)

# Graduation modifiers to detect standalone intensifiers
GRADUATION = taxonomy.get("graduation_modifiers", [])
DELIMITERS = r"[^\w']+"

# Basic triggers/impact clues
TRIGGERS = [
    "intercourse", "sex", "penetration", "menstruation", "period", "ovulate", "ovulation",
    "going to the toilet", "urinate", "bowel movement", "defecate", "poop", "wee", "pee",
    "daily life", "getting up", "moving", "walking", "stand", "sit", "sleep", "breathe", "eat"
]


def tokenize(text):
    return re.split(DELIMITERS, text.lower())


def detect_metaphors(text):
    matches = {}
    entailments = {}
    metaphor_types = set()
    dimensions = set()
    graduation_only = []

    for mtype, data in taxonomy.items():
        # Skip non-dict entries like "graduation_modifiers"
        if not isinstance(data, dict):
            continue

        expressions = data.get("expressions", [])
        matched = [expr for expr in expressions if re.search(
            rf'\b{re.escape(expr)}\b', text.lower())]
        if matched:
            matches[mtype] = matched
            entailments[mtype] = data.get("entailments", [])
            metaphor_types.add(mtype)
            dimensions.update(data.get("dimensions", []))

    if not metaphor_types:
        grad_matched = [mod for mod in GRADUATION if re.search(
            rf'\b{re.escape(mod)}\b', text.lower())]
        if grad_matched:
            graduation_only = grad_matched

    return {
        "metaphor_types": sorted(metaphor_types),
        "matches": matches,
        "entailments": entailments,
        "dimensions": sorted(dimensions),
        "graduation_only": graduation_only
    }



def detect_context(text):
    return sorted({t for t in TRIGGERS if t in text.lower()})


def generate_clinical_info(metaphor_types):
    info = {}
    for mtype in metaphor_types:
        data = taxonomy.get(mtype) or {}
        info[mtype] = {
            "patient_friendly": data.get("patient_friendly", ""),
            "likely_mechanism": data.get("likely_mechanism", ""),
            "clinical_terms": data.get("clinical_terms", []),
            "literature_framing": data.get("literature_framing", "")
        }
    return info


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        description = request.form["description"]
        logging.info(f"User input: {description}")

        metaphor_data = detect_metaphors(description)
        context_data = detect_context(description)

        if metaphor_data["metaphor_types"]:
            clinical = generate_clinical_info(metaphor_data["metaphor_types"])
        elif metaphor_data["graduation_only"]:
            clinical = {
                "graduation_modifiers": {
                    "patient_friendly": "Strong, overwhelming descriptors used to convey extreme distress.",
                    "likely_mechanism": "Indicative of central sensitization or high pain interference.",
                    "clinical_terms": ["pain severity", "pain interference", "functional impact"],
                    "literature_framing": ""
                }
            }
        else:
            clinical = {}

        return render_template("index.html", results={
            "input": description,
            "metaphor_types": metaphor_data["metaphor_types"],
            "matches": metaphor_data["matches"],
            "entailments": metaphor_data["entailments"],
            "dimensions": metaphor_data["dimensions"],
            "graduation_only": metaphor_data["graduation_only"],
            "impact_context": context_data,
            "clinical_rephrasings": clinical
        })

    # For GET requests: show empty form with no results
    return render_template("index.html", results=None)


if __name__ == "__main__":
    app.run(debug=True)
