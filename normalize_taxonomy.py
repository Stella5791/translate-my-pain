import json
import re


def normalize(text):
    """Lowercase and preserve meaningful punctuation like hyphens and apostrophes."""
    return re.sub(r"[^\w\s'\-]", "", text.lower()).strip()


# Load original taxonomy
with open("taxonomy.json", encoding="utf-8") as f:
    taxonomy = json.load(f)

# Normalize metaphor expressions
for cat_name, cat_data in taxonomy.get("metaphor_types", {}).items():
    expressions = cat_data.get("expressions", [])
    normalized = list(set(normalize(expr) for expr in expressions))
    taxonomy["metaphor_types"][cat_name]["expressions"] = sorted(normalized)

# Save normalized taxonomy to a new file
with open("taxonomy_cleaned.json", "w", encoding="utf-8") as f:
    json.dump(taxonomy, f, indent=2, ensure_ascii=False)

print("✅ Normalized expressions saved to taxonomy_cleaned.json")
