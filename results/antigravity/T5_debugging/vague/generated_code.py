import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import os

# Define paths for this specific run
input_file = 'data/raw/dataset.csv'
output_dir = 'results/antigravity/T5_debugging/vague/output/'
os.makedirs(output_dir, exist_ok=True)

# ── Load data ──────────────────────────────────────────────────────────────────
# Use proper path to dataset.csv from project root
df = pd.read_csv(input_file)
print("Loaded dataset:", df.shape)

# ── Clean missing values ───────────────────────────────────────────────────────
# FIX 1: Remove all rows containing '?' in any column
df = df.replace('?', np.nan).dropna()
print("After cleaning:", df.shape)

# ── EDA ────────────────────────────────────────────────────────────────────────
print("\nIncome distribution:\n", df['income'].value_counts())

# Plot 1 — income distribution
plt.figure(figsize=(6, 4))
df['income'].value_counts().plot(kind='bar', color=['steelblue', 'coral'])
plt.title('Income Distribution')
plt.xlabel('Income')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'income_distribution.png'))
plt.close()

# Plot 2 — age by income
plt.figure(figsize=(8, 4))
for label, grp in df.groupby('income'):
    grp['age'].hist(alpha=0.6, bins=25, label=label)
plt.title('Age Distribution by Income')
plt.xlabel('Age')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'age_by_income.png'))
plt.close()

# Plot 3 — hours per week by income
plt.figure(figsize=(7, 4))
sns.boxplot(x='income', y='hours.per.week', data=df)
plt.title('Hours per Week by Income')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'hours_by_income.png'))
plt.close()

print(f"Plots saved to {output_dir}")

# ── Encode categorical columns ─────────────────────────────────────────────────
cat_cols = ['workclass', 'education', 'marital.status', 'occupation',
            'relationship', 'race', 'sex', 'native.country']

# FIX 2: Use separate LabelEncoder for each column
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))

# Encode target (strip whitespace to be safe)
df['income'] = (df['income'].str.strip() == '>50K').astype(int)

# ── Train / test split ─────────────────────────────────────────────────────────
# Drop fnlwgt as it's not a predictive feature (as per project context)
X = df.drop(['income', 'fnlwgt'], axis=1)
y = df['income']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Scale features ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# FIX 3: Use transform() on the test set, not fit_transform()
X_test = scaler.transform(X_test)

# ── Train model ────────────────────────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print("\nAccuracy:", round(accuracy, 4))
print("\nClassification Report:\n", report)

# Save evaluation results
with open(os.path.join(output_dir, 'evaluation_results.txt'), 'w') as f:
    f.write(f"Accuracy: {accuracy:.4f}\n\n")
    f.write("Classification Report:\n")
    f.write(report)
