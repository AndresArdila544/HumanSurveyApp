import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load CSV
file_path = "./Human_survey/demographics.csv"  # Change to your actual file
df = pd.read_csv(file_path)

# Categorize experience
def categorize_experience(years):
    try:
        years = int(years)
        if years < 3:
            return 'Junior'
        elif years < 7:
            return 'Mid'
        else:
            return 'Senior'
    except:
        return 'Unknown'

df['experience_level'] = df['experience_years'].apply(categorize_experience)

# Group and pivot
summary = df.groupby(['experience_level', 'python_skill_level']).size().reset_index(name='count')
pivot_table = summary.pivot(index='experience_level', columns='python_skill_level', values='count').fillna(0).astype(int)

# Ensure order
experience_order = ['Junior', 'Mid', 'Senior']
pivot_table = pivot_table.reindex(experience_order)

ordered_skills = ['beginner', 'intermediate', 'expert']
for skill in ordered_skills:
    if skill not in pivot_table.columns:
        pivot_table[skill] = 0
pivot_table = pivot_table[ordered_skills]

# Experience labels with years
experience_labels = {
    'Junior': 'Junior (0–3 years)',
    'Mid': 'Mid (3–7 years)',
    'Senior': 'Senior (7+ years)'
}
labeled_xticks = [experience_labels.get(label, label) for label in pivot_table.index]

# Adjust bars to show tiny bars for 0s
adjusted_pivot = pivot_table.applymap(lambda x: 0.2 if x == 0 else x)

# Amazon badge colors for Python skill levels
skill_level_colors = {
    'beginner': '#146eb4',     # Blue
    'intermediate': '#ffcc00', # Yellow
    'expert': '#d62d20'        # Red
}

### 1. Grouped Bar Chart with Dynamic Y-Limit
x = np.arange(len(pivot_table.index))
width = 0.25
max_grouped_val = pivot_table.values.max()
grouped_ylim = max_grouped_val + (0.2 * max_grouped_val)

fig, ax = plt.subplots(figsize=(10, 6))
for i, skill in enumerate(ordered_skills):
    values = adjusted_pivot[skill]
    bars = ax.bar(x + i * width, values, width, label=skill.capitalize(), color=skill_level_colors[skill])
    for bar, actual_value in zip(bars, pivot_table[skill]):
        height = bar.get_height()
        label = f'{int(actual_value)}' if actual_value != 0 else '0'
        ax.text(bar.get_x() + bar.get_width() / 2, height + 0.3, label,
                ha='center', va='bottom', fontsize=9)

ax.set_xlabel('Experience Level')
ax.set_ylabel('Count')
ax.set_title('Python Skill Levels by Experience (Amazon Badge Colors)')
ax.set_xticks(x + width)
ax.set_xticklabels(labeled_xticks)
ax.set_ylim(0, grouped_ylim)
ax.legend(title='Python Skill Level')
ax.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("grouped_python_skill_by_experience.png")
plt.show()

### 2. Bar Chart – Count by Experience Level
experience_count = df['experience_level'].value_counts().reindex(experience_order).fillna(0).astype(int)
max_exp_val = experience_count.max()
exp_ylim = max_exp_val + (0.15 * max_exp_val)

plt.figure(figsize=(8, 5))
bars = plt.bar(experience_count.index, experience_count.values, color='#00b3b3')
for idx, val in enumerate(experience_count.values):
    plt.text(idx, val + (0.02 * max_exp_val), str(val), ha='center')
plt.title('Count by Experience Level')
plt.xlabel('Experience Level')
plt.ylabel('Count')
plt.ylim(0, exp_ylim)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("count_by_experience_level.png")
plt.show()

### 3. Bar Chart – Count by Python Skill Level
skill_level_count = df['python_skill_level'].value_counts().reindex(ordered_skills).fillna(0).astype(int)
max_skill_val = skill_level_count.max()
skill_ylim = max_skill_val + (0.15 * max_skill_val)

plt.figure(figsize=(8, 5))
bars = plt.bar(skill_level_count.index.str.capitalize(), skill_level_count.values,
               color=[skill_level_colors[skill] for skill in ordered_skills])
for idx, val in enumerate(skill_level_count.values):
    plt.text(idx, val + (0.02 * max_skill_val), str(val), ha='center')
plt.title('Count by Python Skill Level')
plt.xlabel('Python Skill Level')
plt.ylabel('Count')
plt.ylim(0, skill_ylim)
plt.grid(axis='y', linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("count_by_python_skill_level.png")
plt.show()
