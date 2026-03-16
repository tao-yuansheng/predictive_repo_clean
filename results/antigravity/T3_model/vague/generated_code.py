import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Define paths
input_file = 'results/antigravity/T1_ingestion/vague/output/cleaned_dataset.csv'
output_dir = 'results/antigravity/T3_model/vague/output/'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def train_and_evaluate(df):
    # 1. Preprocessing
    # Target encoding
    le = LabelEncoder()
    df['income'] = le.fit_transform(df['income']) # <=50K: 0, >50K: 1
    
    # Feature selection - dropping redundant/non-predictive columns
    # education and education.num are redundant, fnlwgt is not useful
    X = df.drop(['income', 'education', 'fnlwgt'], axis=1)
    y = df['income']
    
    # One-hot encoding for categorical features
    X = pd.get_dummies(X, drop_first=True)
    
    # 2. Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Model Training (Logistic Regression as baseline)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    # 4. Evaluation
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)
    
    # Save results to text file
    with open(os.path.join(output_dir, 'model_results.txt'), 'w') as f:
        f.write(f"Baseline Logistic Regression Model\n")
        f.write(f"Accuracy: {accuracy:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(report)
    
    # 5. Plot Confusion Matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Confusion Matrix')
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'))
    plt.close()
    
    # 6. Feature Importance (Coefficients)
    coef_df = pd.DataFrame({'Feature': X.columns, 'Coefficient': model.coef_[0]})
    coef_df = coef_df.sort_values(by='Coefficient', ascending=False)
    coef_df.to_csv(os.path.join(output_dir, 'feature_coefficients.csv'), index=False)

if __name__ == "__main__":
    if os.path.exists(input_file):
        df = pd.read_csv(input_file)
        train_and_evaluate(df)
        print(f"Model training and evaluation completed. Outputs saved to: {output_dir}")
    else:
        print(f"Error: {input_file} not found.")
