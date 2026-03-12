# buggy_pipeline.py
# Adult Income dataset — EDA, preprocessing, and baseline model
# NOTE: This script contains bugs. Your task is to find and fix them.

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# ── Load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv('../../data/raw/dataset.csv')
print("Loaded dataset:", df.shape)

# ── Clean missing values ───────────────────────────────────────────────────────
# BUG 1: Only removes '?' from 'workclass' — 'occupation' and 'native.country'
# also contain '?' and are not cleaned. Should be:
#   df = df[~(df == '?').any(axis=1)]
df = df[df['workclass'] != '?']
print("After cleaning:", df.shape)

# ── EDA ────────────────────────────────────────────────────────────────────────
print("\nIncome distribution:\n", df['income'].value_counts())
print("\nAge stats:\n", df['age'].describe())

import os
os.makedirs('output', exist_ok=True)

# Plot 1 — income distribution
plt.figure(figsize=(6, 4))
df['income'].value_counts().plot(kind='bar', color=['steelblue', 'coral'])
plt.title('Income Distribution')
plt.xlabel('Income')
plt.ylabel('Count')
plt.tight_layout()
plt.savefig('output/income_distribution.png')
plt.close()

# Plot 2 — age by income
plt.figure(figsize=(8, 4))
for label, grp in df.groupby('income'):
    grp['age'].hist(alpha=0.6, bins=25, label=label)
plt.title('Age Distribution by Income')
plt.xlabel('Age')
plt.legend()
plt.tight_layout()
plt.savefig('output/age_by_income.png')
plt.close()

# Plot 3 — hours per week distribution
plt.figure(figsize=(7, 4))
sns.boxplot(x='income', y='hours.per.week', data=df)
plt.title('Hours per Week by Income')
plt.tight_layout()
plt.savefig('output/hours_by_income.png')
plt.close()

print("Plots saved to output/")

# ── Encode categorical columns ─────────────────────────────────────────────────
cat_cols = ['workclass', 'education', 'marital.status', 'occupation',
            'relationship', 'race', 'sex', 'native.country']

# BUG 2: A single LabelEncoder is reused across all columns.
# Each call to fit_transform overwrites the previous mapping — the encoder
# no longer holds a valid inverse mapping for any column except the last.
# Fix: use a separate LabelEncoder instance per column.
le = LabelEncoder()
for col in cat_cols:
    df[col] = le.fit_transform(df[col])

# Encode target
df['income'] = (df['income'].str.strip() == '>50K').astype(int)

# ── Train / test split ─────────────────────────────────────────────────────────
X = df.drop(['income', 'fnlwgt'], axis=1)
y = df['income']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Scale features ─────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# BUG 3: fit_transform is called on the test set instead of transform.
# This re-fits the scaler on test data, causing data leakage — the test set
# is scaled using its own mean/std rather than the training set's.
# Fix: X_test = scaler.transform(X_test)
X_test = scaler.fit_transform(X_test)

# ── Train model ────────────────────────────────────────────────────────────────
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 4))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
