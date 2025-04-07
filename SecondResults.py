import pandas as pd

# Load the responses data
responses_df = pd.read_csv("./Human_survey/responses.csv")

# Load the survey index data
survey_index_df = pd.read_csv("./Human_survey/survey_index.csv")

# Print basic info (optional)
print("Responses DataFrame:")
print(responses_df.head())

print("\nSurvey Index DataFrame:")
print(survey_index_df.head())

original_images = {}
refactored_images = {}

for index, row in survey_index_df.iterrows():
    image_name = row['original_image']
    original_images[image_name] = True
    refactored_images[row['refactored_image']] = True

print('Original Image Size:', len(original_images))
print('Refactored Image Size:', len(refactored_images))

no_preference = 0
original_image_count = 0
refactored_image_count = 0

for index, row in responses_df.iterrows():
    chosen = row['chosen']

    if chosen == 'C':
        no_preference += 1
    elif chosen == 'A':
        image_name = row['image_A']
        if image_name in original_images:
            original_image_count += 1
        elif image_name in refactored_images:
            refactored_image_count += 1
    elif chosen == 'B':
        image_name = row['image_B']
        if image_name in original_images:
            original_image_count += 1
        elif image_name in refactored_images:
            refactored_image_count += 1

print('No Preference:', no_preference)
print('Original Image Count:', original_image_count)
print('Refactored Image Count:', refactored_image_count)

import matplotlib.pyplot as plt

# User preference counts
counts = {
    "Original Code": original_image_count,
    "Refactored Code": refactored_image_count,
    "No Preference": no_preference,
}

# Extract labels and values
labels = list(counts.keys())
values = list(counts.values())
max_height = max(values)

# Plotting
plt.figure(figsize=(8, 5))
bars = plt.bar(labels, values)
plt.title("User Preferences for Code Images")
plt.xlabel("Choice")
plt.ylabel("Number of Selections")
plt.ylim(0, max_height + 10)  # Add headroom above tallest bar
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add numerical values on top of each bar
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width() / 2, height + 1, str(height),
             ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()

from collections import defaultdict

# Initialize counters
refactored_reason_counts = defaultdict(int)
original_reason_counts = defaultdict(int)

# Process each response
for _, row in responses_df.iterrows():
    choice = row["chosen"]
    reasons_raw = str(row.get("reason", "")).strip().lower()

    # Skip if choice is not A or B, or if reason is missing
    if choice not in ["A", "B"] or not reasons_raw:
        continue

    # Determine selected image based on user's choice
    selected_image = row["image_A"] if choice == "A" else row["image_B"]

    # Determine whether selected image is original or refactored
    if selected_image in refactored_images:
        image_type = "refactored"
    elif selected_image in original_images:
        image_type = "original"
    else:
        continue

    # Split reasons and count valid ones
    for reason in reasons_raw.split(";"):
        reason = reason.strip()
        if reason in ["concise", "readable", "maintainable"]:
            if image_type == "refactored":
                refactored_reason_counts[reason] += 1
            elif image_type == "original":
                original_reason_counts[reason] += 1

# Print results
print("\nRefactored Image Reason Counts:")
for reason, count in refactored_reason_counts.items():
    print(f"- {reason.capitalize()}: {count}")

print("\nOriginal Image Reason Counts:")
for reason, count in original_reason_counts.items():
    print(f"- {reason.capitalize()}: {count}")

import matplotlib.pyplot as plt

# Use computed reason counts directly
refactored_data = dict(refactored_reason_counts)
original_data = dict(original_reason_counts)

# Plot for Refactored Code
refactored_labels = list(refactored_data.keys())
refactored_values = list(refactored_data.values())

plt.figure(figsize=(7, 5))
bars = plt.bar(refactored_labels, refactored_values, color='teal')
plt.title("Refactored Code - Reason Counts")
plt.xlabel("Reason")
plt.ylabel("Count")
plt.ylim(0, max(refactored_values) + 5)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, str(height),
             ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.show()

# Plot for Original Code
original_labels = list(original_data.keys())
original_values = list(original_data.values())

plt.figure(figsize=(7, 5))
bars = plt.bar(original_labels, original_values, color='orange')
plt.title("Original Code - Reason Counts")
plt.xlabel("Reason")
plt.ylabel("Count")
plt.ylim(0, max(original_values) + 5)
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, height + 0.5, str(height),
             ha='center', va='bottom', fontsize=10)
plt.tight_layout()
plt.show()
