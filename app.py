from flask import Flask, render_template, request
from tagger_logic import (
    tag_pain_description,
    generate_patient_summary,
    generate_doctor_summary,
    generate_entailment_summary
)

from taxonomy import taxonomy
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your_default_secret")


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    description = ""
    name = ""
    duration = ""

    if request.method == "POST":
        description = request.form.get("description", "").strip()
        name = request.form.get("name", "").strip()
        duration = request.form.get("duration", "").strip()

        if description:
            try:
                results = tag_pain_description(
                    description,
                    name=name if name else None,
                    duration=duration if duration else None
                )

                results["input"] = description
                results["plain_summary"] = generate_patient_summary(results)
                results["doctor_narrative"] = generate_doctor_summary(results)
                results["entailment_summary"] = generate_entailment_summary(
                    results.get("entailments", {})
                )

            except Exception as e:
                print(f"[Error] Failed to process description: {e}")
                results = {
                    "input": description,
                    "plain_summary": "Could not generate patient summary.",
                    "doctor_narrative": "Could not generate doctor notes.",
                    "entailment_summary": "Could not generate entailment summary.",
                    "user_info": {
                        "name": name if name else None,
                        "duration": duration if duration else None
                    },
                    "error": "There was an error processing your input."
                }

    return render_template("index.html", results=results)


@app.route("/samples")
def samples():
    try:
        sample_categories = {
            cat: data.get("expressions", [])[:4]
            for cat, data in taxonomy.get("metaphor_types", {}).items()
        }
    except Exception as e:
        print(f"[Warning] Could not load samples: {e}")
        sample_categories = {}

    return render_template("samples.html", sample_categories=sample_categories)


@app.route("/evidence")
def evidence():
    return render_template("evidence.html")


if __name__ == "__main__":
    app.run(debug=True)
