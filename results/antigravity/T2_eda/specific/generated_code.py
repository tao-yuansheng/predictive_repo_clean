import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy.stats import skew, kurtosis

# Define paths
input_file = 'data/raw/dataset.csv'
output_dir = 'results/antigravity/T2_eda/specific/output/'

# Create output directory
os.makedirs(output_dir, exist_ok=True)

def perform_comprehensive_eda():
    # 1. Data Overview
    print("--- 1. Data Overview ---")
    df = pd.read_csv(input_file)
    df = df.replace('?', np.nan)
    print(f"Shape: {df.shape}")
    print("\nDtypes:")
    print(df.dtypes)
    
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df)) * 100
    print("\nMissing values per column:")
    print(pd.DataFrame({'Count': missing_counts, 'Percentage': missing_pct})[missing_counts > 0])

    # 2. Numeric Column Analysis
    print("\n--- 2. Numeric Column Analysis ---")
    numeric_cols = ['age', 'fnlwgt', 'education.num', 'capital.gain', 'capital.loss', 'hours.per.week']
    for col in numeric_cols:
        data = df[col].dropna()
        m, med, s = data.mean(), data.median(), data.std()
        sk, ku = skew(data), kurtosis(data)
        
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).sum()
        
        print(f"\n{col.upper()}:")
        print(f"Mean: {m:.2f}, Median: {med:.2f}, Std: {s:.2f}")
        print(f"Skewness: {sk:.2f}, Kurtosis: {ku:.2f}")
        print(f"Outliers (IQR): {outliers}")
        
        plt.figure(figsize=(8, 4))
        sns.histplot(data, kde=True)
        plt.title(f'Distribution of {col}\nSkewness: {sk:.2f}')
        plt.savefig(os.path.join(output_dir, f'dist_{col}.png'))
        plt.close()
        
        if col in ['capital.gain', 'capital.loss']:
            zero_pct = (df[col] == 0).sum() / len(df) * 100
            print(f"NOTE: {col} is heavily zero-inflated ({zero_pct:.2f}% zeros).")

    # 3. Categorical Column Analysis
    print("\n--- 3. Categorical Column Analysis ---")
    cat_cols = ['workclass', 'education', 'marital.status', 'occupation', 'relationship', 'race', 'sex', 'native.country']
    for col in cat_cols:
        counts = df[col].value_counts()
        print(f"\n{col.upper()} (nunique: {df[col].nunique()}):")
        top_cat_pct = counts.iloc[0] / len(df) * 100
        if top_cat_pct > 70:
            print(f"FLAG: {col} is dominated by '{counts.index[0]}' ({top_cat_pct:.2f}%).")
        
        plt.figure(figsize=(10, 5))
        counts.head(10).plot(kind='bar')
        plt.title(f'Top 10 Categories in {col}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'barplot_{col}.png'))
        plt.close()

    # 4. Target Variable
    print("\n--- 4. Target Variable ---")
    income_counts = df['income'].value_counts()
    ratio = income_counts.iloc[0] / income_counts.iloc[1]
    print(f"Income distribution:\n{income_counts}")
    print(f"Class imbalance ratio (<=50K : >50K): {ratio:.2f} : 1")
    print("NOTE: The imbalance (~3:1) may lead the model to favour the majority class (<=50K).")
    
    plt.figure(figsize=(6, 4))
    sns.countplot(x='income', data=df)
    plt.title('Target Variable (income) Distribution')
    plt.savefig(os.path.join(output_dir, 'income_distribution.png'))
    plt.close()

    # 5. Correlation & Feature Relevance
    print("\n--- 5. Correlation & Feature Relevance ---")
    df_corr = df.copy()
    df_corr['income_bin'] = (df_corr['income'].str.strip() == '>50K').astype(int)
    
    # Correlation Heatmap (numeric only)
    plt.figure(figsize=(10, 8))
    numeric_for_corr = df_corr[numeric_cols + ['income_bin']]
    sns.heatmap(numeric_for_corr.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Heatmap')
    plt.savefig(os.path.join(output_dir, 'correlation_heatmap.png'))
    plt.close()
    
    # Top correlations
    corrs = numeric_for_corr.corr()['income_bin'].sort_values(ascending=False)
    print("\nTop numeric correlations with income:")
    print(corrs)

    # 6. Bivariate Analysis
    print("\n--- 6. Bivariate Analysis ---")
    # Top 3 numeric correlates: education.num, age, hours.per.week
    top_3 = ['education.num', 'age', 'hours.per.week']
    for feat in top_3:
        plt.figure(figsize=(8, 6))
        sns.boxplot(x='income', y=feat, data=df)
        plt.title(f'{feat} vs Income')
        plt.savefig(os.path.join(output_dir, f'bivariate_{feat}.png'))
        plt.close()

    # 7. Leakage Flags
    print("\n--- 7. Leakage Flags ---")
    flags = {
        'fnlwgt': "Derived from census sampling and not a demographic feature, but not direct target leakage.",
        'education.num': "Direct ordinal encoding of 'education', redundancy can inflate importance but not strict leakage.",
        'capital.gain/loss': "Strong indicators of financial status that might be proxies for the income target."
    }
    for col, reason in flags.items():
        print(f"- {col}: {reason}")

    # 8. Summary
    summary = """
    SUMMARY OF EDA FINDINGS:
    - Key Patterns: Income is positively correlated with age, education years, and hours worked.
    - Zero-inflation: Capital gain/loss have >90% zeros, needing specific feature engineering (e.g., binary flags).
    - Class Imbalance: 3:1 ratio (<=50K : >50K) suggests need for stratified splitting or class weights.
    - Preprocessing Needs:
        1. Impute missing values in workclass, occupation, and native.country.
        2. Encode categorical variables (One-hot or Label).
        3. Standardise numeric features due to varying scales (e.g., age vs fnlwgt).
        4. Handle outliers in numeric features using clipping or robust scaling.
    """
    print("\n" + summary)

if __name__ == "__main__":
    perform_comprehensive_eda()
