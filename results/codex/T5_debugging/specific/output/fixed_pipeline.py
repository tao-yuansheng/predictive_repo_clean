# fixed_pipeline.py
# Adult Income dataset - EDA, preprocessing, and baseline model

import os
import tempfile
from pathlib import Path

# FIX [6]: Point Matplotlib at a writable temp config directory so plotting works in fresh headless environments.
os.environ.setdefault("MPLCONFIGDIR", tempfile.gettempdir())

import pandas as pd
# FIX [6]: Use a non-interactive backend so plot saving does not depend on a GUI session.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# -- Load data -----------------------------------------------------------------
# FIX [1]: Resolve the repository root from the script location so the pipeline runs from any working directory.
REPO_ROOT = Path(__file__).resolve().parent
# FIX [1]: Walk upward until the dataset path is found instead of relying on the caller's current directory.
while REPO_ROOT != REPO_ROOT.parent and not (REPO_ROOT / 'data' / 'raw' / 'dataset.csv').exists():
    REPO_ROOT = REPO_ROOT.parent
# FIX [1]: Read the dataset from the discovered repository root.
df = pd.read_csv(REPO_ROOT / 'data' / 'raw' / 'dataset.csv')
print("Loaded dataset:", df.shape)

# -- Clean missing values ------------------------------------------------------
# FIX [2]: Remove every row containing the '?' missing-value sentinel so occupation and native.country are cleaned too.
df = df[~(df == '?').any(axis=1)].copy()
print("After cleaning:", df.shape)

# -- EDA -----------------------------------------------------------------------
print("\nIncome distribution:\n", df['income'].value_counts())
print("\nAge stats:\n", df['age'].describe())

# FIX [3]: Save outputs beside this script instead of in the caller's working directory.
OUTPUT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Plot 1 - income distribution
plt.figure(figsize=(6, 4))
df['income'].value_counts().plot(kind='bar', color=['steelblue', 'coral'])
plt.title('Income Distribution')
plt.xlabel('Income')
plt.ylabel('Count')
plt.tight_layout()
# FIX [3]: Write plot files into the script output directory.
plt.savefig(OUTPUT_DIR / 'income_distribution.png')
plt.close()

# Plot 2 - age by income
plt.figure(figsize=(8, 4))
for label, grp in df.groupby('income'):
    grp['age'].hist(alpha=0.6, bins=25, label=label)
plt.title('Age Distribution by Income')
plt.xlabel('Age')
plt.legend()
plt.tight_layout()
# FIX [3]: Write plot files into the script output directory.
plt.savefig(OUTPUT_DIR / 'age_by_income.png')
plt.close()

# Plot 3 - hours per week distribution
plt.figure(figsize=(7, 4))
sns.boxplot(x='income', y='hours.per.week', data=df)
plt.title('Hours per Week by Income')
plt.tight_layout()
# FIX [3]: Write plot files into the script output directory.
plt.savefig(OUTPUT_DIR / 'hours_by_income.png')
plt.close()

print("Plots saved to", OUTPUT_DIR)

# -- Encode categorical columns ------------------------------------------------
cat_cols = ['workclass', 'education', 'marital.status', 'occupation',
            'relationship', 'race', 'sex', 'native.country']

# FIX [4]: Keep one LabelEncoder per categorical column so each mapping remains valid.
encoders = {}
for col in cat_cols:
    # FIX [4]: Fit and store a separate encoder for each categorical feature.
    encoders[col] = LabelEncoder()
    df[col] = encoders[col].fit_transform(df[col])

# Encode target
df['income'] = (df['income'].str.strip() == '>50K').astype(int)

# -- Train / test split --------------------------------------------------------
X = df.drop(['income', 'fnlwgt'], axis=1)
y = df['income']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -- Scale features ------------------------------------------------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

# FIX [5]: Apply the scaler fitted on the training data to the test set instead of re-fitting on test data.
X_test = scaler.transform(X_test)

# -- Train model ---------------------------------------------------------------
model = LogisticRegression(max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# -- Evaluate ------------------------------------------------------------------
y_pred = model.predict(X_test)
print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 4))
print("\nClassification Report:\n", classification_report(y_test, y_pred))
