from flask import Flask, render_template, request
import logging
from tagger_logic import tag_pain_description  # Use the main tagging function

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        if not description:
            return render_template("index.html", results={"error": "Please provide a pain description."})

        logging.info(f"User input: {description}")
        result = tag_pain_description(description)
        return render_template("index.html", results=result)

    # For GET requests: show empty form with no results
    return render_template("index.html", results=None)

# Optional future feature: PDF export
# from flask import make_response
# from weasyprint import HTML
# @app.route("/download-pdf", methods=["POST"])
# def download_pdf():
#     description = request.form.get("description", "")
#     results = tag_pain_description(description)
#     html = render_template("pdf_template.html", results=results)
#     pdf = HTML(string=html).write_pdf()
#     response = make_response(pdf)
#     response.headers['Content-Type'] = 'application/pdf'
#     response.headers['Content-Disposition'] = 'attachment; filename=translated_pain_report.pdf'
#     return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
