import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import os

# Define paths
input_file = 'data/raw/dataset.csv'
output_dir = 'results/antigravity/T4_leakage/vague/output/'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def audit_for_leakage(df):
    # 1. Preprocessing for analysis
    # Target encoding
    le_target = LabelEncoder()
    df['income_encoded'] = le_target.fit_transform(df['income'].astype(str))
    
    # 2. Correlation Analysis
    # Get numeric columns and encode categorical ones temporarily for correlation
    df_encoded = df.copy()
    # Drop the original income string column to avoid corr errors
    if 'income' in df_encoded.columns:
        df_encoded = df_encoded.drop('income', axis=1)
        
    for col in df_encoded.select_dtypes(include=['object']).columns:
        df_encoded[col] = LabelEncoder().fit_transform(df_encoded[col].astype(str))
    
    correlations = df_encoded.corr()['income_encoded'].sort_values(ascending=False)
    correlations.to_csv(os.path.join(output_dir, 'feature_correlations.csv'))
    
    # 3. Leakage Detection Logic
    leakage_findings = []
    
    for feat, corr in correlations.items():
        if feat != 'income_encoded':
            if abs(corr) > 0.8:
                leakage_findings.append(f"HIGH CORRELATION: {feat} has a correlation of {corr:.4f} with income. This is highly suspicious.")
            elif abs(corr) > 0.5:
                leakage_findings.append(f"MODERATE-HIGH CORRELATION: {feat} has a correlation of {corr:.4f}. Worth investigating.")

    # 4. Summary Report
    with open(os.path.join(output_dir, 'leakage_report.txt'), 'w') as f:
        f.write("Data Leakage Audit Report\n")
        f.write("=========================\n\n")
        
        if not leakage_findings:
            f.write("No obvious high-correlation leakage detected based on simple correlation analysis.\n")
        else:
            for finding in leakage_findings:
                f.write(f"- {finding}\n")
        
        f.write("\nManual Audit Notes:\n")
        f.write("1. 'fnlwgt' (final weight) is a census weight and should be excluded from modelling.\n")
        f.write("2. 'capital.gain' and 'capital.loss' are financial outcomes.\n")
        f.write("3. 'education.num' and 'education' are redundant.\n")
        f.write("4. No features appear to be 'future' information.\n")

if __name__ == "__main__":
    if os.path.exists(input_file):
        df = pd.read_csv(input_file, na_values='?')
        audit_for_leakage(df)
        print(f"Leakage audit completed. Outputs saved to: {output_dir}")
    else:
        print(f"Error: {input_file} not found.")
