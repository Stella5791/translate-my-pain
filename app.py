from flask import Flask, render_template, request, flash
from tagger_logic import (
    tag_pain_description,
    generate_patient_summary,
    generate_doctor_summary,
    generate_research_summary,
    generate_entailment_summary  # ← Ensure this is present in tagger_logic.py
)

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Needed for flashing messages


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        name = request.form.get("name", "").strip()
        duration = request.form.get("duration", "").strip()

        if not description:
            flash("Please enter a pain description.", "warning")
        else:
            results = tag_pain_description(
                description,
                name=name if name else None,
                duration=duration if duration else None
            )
            results["input"] = description

            # Existing summaries
            results["patient_narrative"] = generate_patient_summary(results)
            results["doctor_narrative"] = generate_doctor_summary(results)
            results["research_narrative"] = generate_research_summary(results)

            results["entailment_summary"] = generate_entailment_summary(
                results["entailments"])


    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
