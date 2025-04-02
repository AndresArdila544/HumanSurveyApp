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
DEMOGRAPHICS_FILE = "Human_survey/demographics.csv"

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
        .subtitle { font-size: 0.95rem; color: #666; margin-bottom: 15px; }
    </style>
</head>
<body class="container py-4">
    <h1 class="mb-2">Code Refactoring Preference Survey</h1>

<p>This survey is part of a research study on how people perceive automatically refactored Python code. We are investigating how readability, maintainability, and complexity influence code preferences.</p>
<p>Your participation is anonymous. Your feedback will contribute to understanding the effectiveness of LLMs as refactoring tools.</p>
<p><strong>Instructions:</strong> You'll see 10 pairs of Python code snippets. For each pair, select the version you prefer.</p>

<hr>




    <form method="post">
    <!-- Demographics -->
<div class="mb-3">
  <label for="experience" class="form-label"><strong>How many years of experience do you have with programming?</strong></label>
  <input type="number" class="form-control" name="experience" id="experience" min="0" max="50" required>
</div>

<div class="mb-4">
  <label for="python_skill" class="form-label"><strong>How familiar are you with Python?</strong></label>
  <select class="form-select" name="python_skill" id="python_skill" required>
    <option value="">Select...</option>
    <option value="beginner">Beginner</option>
    <option value="intermediate">Intermediate</option>
    <option value="expert">Expert</option>
  </select>
</div>
        {% for pair in pairs %}
            <div class="pair-block">
                <h5>Pair {{ loop.index }}</h5>
                <p class="subtitle">
                    Please choose the option you prefer.
                </p>

                <div class="mb-2">
                    <label class="form-label">Option A</label><br>
                    <img src="{{ url_for('serve_image', filename=pair[0]) }}" alt="Option A">
                </div>

                <div class="mb-2">
                    <label class="form-label">Option B</label><br>
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
                <!-- Reason checkboxes -->
<div class="mt-2">
  <p><strong>Why?</strong> (Select all that apply)</p>
  <div class="form-check">
    <input class="form-check-input" type="checkbox" name="reason_{{ loop.index0 }}[]" value="concise">
    <label class="form-check-label">More concise</label>
  </div>
  <div class="form-check">
    <input class="form-check-input" type="checkbox" name="reason_{{ loop.index0 }}[]" value="readable">
    <label class="form-check-label">More readable</label>
  </div>
  <div class="form-check">
    <input class="form-check-input" type="checkbox" name="reason_{{ loop.index0 }}[]" value="maintainable">
    <label class="form-check-label">Easier to maintain</label>
  </div>
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

import uuid 
from flask import make_response
import os

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
        experience = request.form.get("experience")
        python_skill = request.form.get("python_skill")
        submission_id = str(uuid.uuid4())
        response_rows = []
        for i, (img_a, img_b) in enumerate(pairs):
            choice = request.form.get(f"pair_{i}")
            if choice is None:
                return "❌ Please answer all questions."
            reasons = request.form.getlist(f"reason_{i}[]")  # Collect all selected reasons
            response_rows.append([
                submission_id,
                f"pair_{i+1}",
                img_a,
                img_b,
                choice,
                ";".join(reasons) if reasons else ""
            ])

        write_demo_header = not os.path.exists(DEMOGRAPHICS_FILE)
        with open(DEMOGRAPHICS_FILE, "a", encoding="utf-8", newline='') as f:
            writer = csv.writer(f)
            if write_demo_header:
                writer.writerow(["submission_id", "experience_years", "python_skill_level"])
            writer.writerow([submission_id, experience, python_skill])

        write_header = not os.path.exists(RESPONSE_FILE)
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
