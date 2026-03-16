import pandas as pd
import numpy as np
import json
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn

# Set random seeds for reproducibility
np.random.seed(42)

# Define paths
input_file = 'results/antigravity/T1_ingestion/specific/output/dataset_clean.csv'
output_dir = 'results/antigravity/T3_model/specific/output/'

# Create output directory
os.makedirs(output_dir, exist_ok=True)

def run_baseline_model():
    # 1. Load Data
    print("--- 1. Load Data ---")
    if os.path.exists(input_file):
        df = pd.read_csv(input_file)
    else:
        df = pd.read_csv('data/raw/dataset.csv').replace('?', np.nan).drop_duplicates()
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
    
    print(f"Dataset shape: {df.shape}")
    
    df['income'] = df['income'].str.strip()
    le_target = LabelEncoder()
    df['income'] = le_target.fit_transform(df['income']) 
    
    X = df.drop('income', axis=1)
    y = df['income']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # 2. Preprocessing
    print("\n--- 2. Preprocessing ---")
    cat_cols = X.select_dtypes(include=['object']).columns
    for col in cat_cols:
        le = LabelEncoder()
        # Fit on BOTH train and test to handle rare categories like 'Holand-Netherlands'
        full_series = pd.concat([X_train[col], X_test[col]]).astype(str)
        le.fit(full_series)
        X_train[col] = le.transform(X_train[col].astype(str))
        X_test[col] = le.transform(X_test[col].astype(str))
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 3. Baseline Model
    print("\n--- 3. Baseline Model ---")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # 4. Evaluation
    print("\n--- 4. Evaluation ---")
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "roc_auc": float(roc_auc_score(y_test, y_prob))
    }
    
    print(f"Metrics: {metrics}")
    
    with open(os.path.join(output_dir, 'task3_results.json'), 'w') as f:
        json.dump(metrics, f, indent=4)
    
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()
    
    # 5. Output
    joblib.dump(model, os.path.join(output_dir, 'baseline_model.pkl'))
    with open(os.path.join(output_dir, 'requirements_task3.txt'), 'w') as f:
        f.write(f"pandas=={pd.__version__}\n")
        f.write(f"numpy=={np.__version__}\n")
        f.write(f"scikit-learn=={sklearn.__version__}\n")
        f.write(f"joblib=={joblib.__version__}\n")

if __name__ == "__main__":
    run_baseline_model()
