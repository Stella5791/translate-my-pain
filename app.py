from tagger_logic import tag_pain_description
from flask import Flask, render_template, request, make_response
from weasyprint import HTML
import sys
import os

# Add path to find tagger_logic.py
sys.path.append(
    '/Users/stellabullo/my_projects/health-projects/metaphor-tagger')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    if request.method == 'POST':
        text = request.form['description']
        results = tag_pain_description(text)
    return render_template('index.html', results=results)


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    text = request.form['description']
    results = tag_pain_description(text)
    rendered = render_template('pdf_template.html', results=results)
    pdf = HTML(string=rendered).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=translated_pain_report.pdf'
    return response


if __name__ == '__main__':
    app.run(debug=True)
