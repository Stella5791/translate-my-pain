from tagger_logic import tag_pain_description  # ✅ Now this will work
from flask import Flask, render_template, request
import sys
import os

# ✅ Tell Python where to find tagger_logic.py
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


if __name__ == '__main__':
    app.run(debug=True)
