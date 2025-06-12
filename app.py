from flask import Flask, render_template, request
from tagger_logic import tag_pain_description

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    if request.method == "POST":
        description = request.form.get("description")
        name = request.form.get("name")
        duration = request.form.get("duration")

        results = tag_pain_description(
            description,  # no keyword here
            name=name if name else None,
            duration=duration if duration else None
        )

        results["input"] = description  # add original input for display
    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
