# Explain My Pain 🩺🧠

**Explain My Pain** is a patient-centered web app that uses NLP (Natural Language Processing) to identify and categorize metaphorical descriptions of chronic pelvic pain, especially in endometriosis. It transforms raw patient language into structured outputs to support doctor–patient communication, clinical understanding, and linguistic research.

---

## 🧩 What It Does

- **Analyzes metaphorical pain language** using a curated taxonomy
- **Tags metaphors** with experiential and emotional dimensions
- **Generates outputs** for:
  - Patients ("How this might feel to you")
  - Doctors ("Clinical notes")
  - Researchers ("Notes on metaphor types")
- **Supports PDF export** of a structured symptom summary

---

## 🛠️ Tech Stack

- **Python** (Flask)
- **Regex-based NLP** with a custom metaphor taxonomy
- **HTML/CSS** (Jinja templates)
- **JSON-based knowledge base** for metaphor, entailments, and clinical rephrasings
- **Lightweight front-end** with responsive design
- **Print-ready PDF support**

---

## 📂 Project Structure

```
.
├── app.py                 # Flask app with routes and rendering
├── tagger_logic.py        # Core metaphor tagging logic
├── entailments.py         # Retrieves entailments for each metaphor
├── taxonomy.json          # Metaphor categories and expressions
├── clinical_map.json      # Clinical summaries and medical interpretations
├── templates/
│   ├── index.html         # Main app interface
│   ├── pdf_template.html  # Layout for printable output
│   ├── samples.html       # Example input descriptions
│   └── evidence.html      # Background sources and researcher info
└── static/                # (Optional) CSS and media assets
```

---

## 🧪 Example Use Case

**Input:**

> "When I ovulate, it feels like someone is strangling my womb. During my period, it’s like a fireball tearing through me."

**Output:**
- Tags `strangling` → `constriction_pressure`
- Tags `fireball` and `tearing` → `heat`, `violent_action`
- Outputs experiential summaries + clinical phrasing for GP or specialist

---

## 🔍 Who Is It For?

- People with **chronic pelvic pain** or **endometriosis**
- Clinicians seeking **clearer patient symptom narratives**
- Researchers exploring **figurative language and health communication**
- **Employers** looking for real-world NLP + health tech applications

---

## 🚀 How to Run Locally

```bash
# 1. Clone repo and create venv
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Install dependencies
pip install flask

# 3. Run app
python app.py

# 4. Visit in browser
http://127.0.0.1:5000/
```

---

## 🧑‍💻 Developer

**Stella Bullo**  
Python Developer · NLP Specialist · Linguist  
[Portfolio](https://your-portfolio-link.com) · [GitHub](https://github.com/yourusername)

---

## 📚 Research + Ethics

This app was created by a researcher with lived experience of endometriosis. It draws on peer-reviewed studies, patient voices, and ethical considerations in translating metaphorical pain into clinical dialogue.

> Not a diagnostic tool. Outputs are indicative and meant to support—not replace—medical consultation.

---

## 📝 License

MIT License