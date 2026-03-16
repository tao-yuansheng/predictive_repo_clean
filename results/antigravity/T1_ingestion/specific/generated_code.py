# Requirements: pandas, numpy, seaborn, matplotlib
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Set random seed for reproducibility
np.random.seed(42)

# Define paths
input_path = 'data/raw/dataset.csv'
output_dir = 'results/antigravity/T1_ingestion/specific/output/'
output_file = os.path.join(output_dir, 'dataset_clean.csv')
heatmap_file = os.path.join(output_dir, 'missingness_heatmap.png')

# Create output directory
os.makedirs(output_dir, exist_ok=True)

def run_specific_ingestion():
    # 1. Data Ingestion
    print("--- 1. Data Ingestion ---")
    df = pd.read_csv(input_path)
    # Replace "?" with np.nan immediately
    df = df.replace('?', np.nan)
    print(f"Loaded dataset shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nColumn dtypes:")
    print(df.dtypes)
    # Checking for mis-typed columns (numeric stored as object)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check if it could be numeric
            try:
                pd.to_numeric(df[col].dropna())
                print(f"FLAG: Column '{col}' is object but appears numeric.")
            except:
                pass

    # 2. Schema Validation
    print("\n--- 2. Schema Validation ---")
    expected_columns = [
        'age', 'workclass', 'fnlwgt', 'education', 'education.num',
        'marital.status', 'occupation', 'relationship', 'race', 'sex',
        'capital.gain', 'capital.loss', 'hours.per.week', 'native.country', 'income'
    ]
    missing_cols = [col for col in expected_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"CRITICAL ERROR: Missing expected columns: {missing_cols}")
    else:
        print("All expected columns are present.")

    print("\nCardinality of categorical columns:")
    cat_cols = df.select_dtypes(include=['object']).columns
    for col in cat_cols:
        print(f"{col}: {df[col].nunique()} unique values")

    # 3. Missingness Audit
    print("\n--- 3. Missingness Audit ---")
    missing_counts = df.isnull().sum()
    missing_pct = (df.isnull().sum() / len(df)) * 100
    missing_report = pd.DataFrame({'Count': missing_counts, 'Percentage': missing_pct})
    print(missing_report[missing_report['Count'] > 0])

    # Visualise missingness
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis')
    plt.title('Missingness Heatmap')
    plt.savefig(heatmap_file)
    plt.close()
    print(f"Missingness heatmap saved to {heatmap_file}")

    # Categorise and Impute
    # <20% missing -> Impute (Numeric: median, Categorical: mode)
    # 20-50% -> Flag for review (None in this dataset typically)
    # >50% -> Drop (None in this dataset typically)
    
    imputed_cols = []
    for col in df.columns:
        pct = missing_pct[col]
        if pct > 0:
            if pct > 50:
                print(f"DROPPING '{col}' due to >50% missingness ({pct:.2f}%)")
                df = df.drop(col, axis=1)
            elif pct >= 20:
                print(f"FLAGGING '{col}' for manual review ({pct:.2f}% missing)")
            else:
                # Impute <20%
                if df[col].dtype in ['int64', 'float64']:
                    median_val = df[col].median()
                    df[col] = df[col].fillna(median_val)
                    imputed_cols.append(f"{col} (median: {median_val})")
                else:
                    mode_val = df[col].mode()[0]
                    df[col] = df[col].fillna(mode_val)
                    imputed_cols.append(f"{col} (mode: {mode_val})")

    # 4. Data Cleaning
    print("\n--- 4. Data Cleaning ---")
    # Duplicate rows
    initial_rows = len(df)
    df = df.drop_duplicates()
    duplicates_removed = initial_rows - len(df)
    print(f"Removed {duplicates_removed} exact duplicate rows.")

    # Outliers (IQR 1.5x rule)
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    capped_counts = {}
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Count values to be capped
        to_cap_lower = (df[col] < lower_bound).sum()
        to_cap_upper = (df[col] > upper_bound).sum()
        capped_counts[col] = to_cap_lower + to_cap_upper
        
        # Cap
        df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

    print("Outliers capped per numeric column:")
    for col, count in capped_counts.items():
        print(f"{col}: {count} values capped")

    # Standardise strings (strip whitespace)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    print("Stripped whitespace from all categorical columns.")

    # 5. Output
    print("\n--- 5. Output ---")
    df.to_csv(output_file, index=False)
    print(f"Cleaned dataset saved to {output_file}")

    print("\n--- FINAL CLEANING REPORT ---")
    print(f"Rows before cleaning: {initial_rows}")
    print(f"Rows after cleaning: {len(df)}")
    print(f"Columns dropped: {list(set(expected_columns) - set(df.columns))}")
    print(f"Columns imputed: {imputed_cols}")
    print(f"Total outliers capped: {sum(capped_counts.values())}")

if __name__ == "__main__":
    run_specific_ingestion()
