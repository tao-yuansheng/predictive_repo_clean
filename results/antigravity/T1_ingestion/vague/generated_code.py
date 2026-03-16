import pandas as pd
import os

# Define paths
input_path = 'data/raw/dataset.csv'
output_dir = 'results/antigravity/T1_ingestion/vague/output/'
output_file = os.path.join(output_dir, 'cleaned_dataset.csv')

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def load_and_clean_data(path):
    # Load dataset, treating '?' as NaN
    df = pd.read_csv(path, na_values='?')
    
    # Basic info before cleaning
    print(f"Initial shape: {df.shape}")
    print("\nMissing values per column:")
    print(df.isnull().sum())
    
    # Strategy: 
    # 1. Drop duplicates if any
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"\nDropped {initial_rows - len(df)} duplicate rows.")
    
    # 2. Handle missing values
    # For this vague prompt, we'll drop rows with missing values to ensure a clean dataset for modelling.
    # Alternatively, we could impute, but dropping is safer for a "vague" instruction to "clean it up".
    df_cleaned = df.dropna()
    print(f"Dropped {len(df) - len(df_cleaned)} rows with missing values.")
    
    # 3. Final validation
    print(f"\nFinal shape: {df_cleaned.shape}")
    
    return df_cleaned

if __name__ == "__main__":
    cleaned_df = load_and_clean_data(input_path)
    
    # Save cleaned dataset
    cleaned_df.to_csv(output_file, index=False)
    print(f"\nCleaned dataset saved to: {output_file}")
