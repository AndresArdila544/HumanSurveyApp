import random
import csv
from pathlib import Path
from flask import Flask, render_template_string, request, redirect, send_from_directory

app = Flask(__name__)

# === CONFIG ===
     # LLMRefactoring/
IMAGE_FOLDER =  "Human_survey"
CSV_INDEX = "Human_survey/survey_index.csv"
NUM_PAIRS = 10
RESPONSE_FILE = "Human_survey/responses.csv"

# === HTML TEMPLATE ===
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Code Refactoring Survey</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .pair-block { margin-bottom: 40px; }
        img { max-width: 100%; height: auto; border: 1px solid #ccc; margin-bottom: 10px; }
    </style>
</head>
<body class="container py-4">
    <h1 class="mb-4">Code Refactoring Preference Survey</h1>
    <form method="post">
        {% for pair in pairs %}
            <div class="pair-block">
                <h5>Pair {{ loop.index }}</h5>
                <div>
                    <label>Option A</label>
                    <img src="{{ url_for('serve_image', filename=pair[0]) }}" alt="Option A">
                </div>
                <div>
                    <label>Option B</label>
                    <img src="{{ url_for('serve_image', filename=pair[1]) }}" alt="Option B">
                </div>
                <div class="form-check mt-2">
                    <input class="form-check-input" type="radio" name="pair_{{ loop.index0 }}" value="A" required>
                    <label class="form-check-label">Prefer A</label>
                </div>
                <div class="form-check mb-4">
                    <input class="form-check-input" type="radio" name="pair_{{ loop.index0 }}" value="B" required>
                    <label class="form-check-label">Prefer B</label>
                </div>
            </div>
        {% endfor %}
        <button type="submit" class="btn btn-primary">Submit</button>
    </form>
</body>
</html>

"""

# === ROUTES ===
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

import uuid  # Add this to your imports at the top
from flask import make_response

@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.cookies.get("has_submitted"):
        return "<h2>✅ You've already submitted. Thank you!</h2>"
    
    with open(CSV_INDEX, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))

    if len(reader) < NUM_PAIRS:
        return f"❌ Not enough image pairs in survey_index.csv. Found {len(reader)}"

    sampled = random.sample(reader, NUM_PAIRS)
    pairs = [(row['original_image'], row['refactored_image']) for row in sampled]

    if request.method == 'POST':
        submission_id = str(uuid.uuid4())
        response_rows = []
        for i, (img_a, img_b) in enumerate(pairs):
            choice = request.form.get(f"pair_{i}")
            if choice is None:
                return "❌ Please answer all questions."
            response_rows.append([submission_id, f"pair_{i+1}", img_a, img_b, choice])

        write_header = not RESPONSE_FILE.exists()
        resp = make_response(redirect("/"))
        resp.set_cookie("has_submitted", "true")
        with open(RESPONSE_FILE, "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["submission_id", "pair", "image_A", "image_B", "chosen"])
            writer.writerows(response_rows)
        return resp  
    
    return render_template_string(HTML_TEMPLATE, pairs=pairs)


if __name__ == '__main__':
    app.run(debug=True)
