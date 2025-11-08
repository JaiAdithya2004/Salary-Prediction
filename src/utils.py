"""Utility helper functions."""
import pandas as pd
import os


def load_data(data_path):
    """
    Load dataset from CSV file.
    
    Args:
        data_path: Path to CSV file
    
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found: {data_path}")
    return pd.read_csv(data_path)


def clean_data(df, target_col="Salary", remove_duplicates=True, handle_missing="drop"):
    """
    Clean dataset by handling missing values and removing duplicates.
    
    Args:
        df: DataFrame to clean
        target_col: Name of target variable column
        remove_duplicates: Whether to remove duplicate records (default: True)
        handle_missing: How to handle missing values - 'drop' or 'fill' (default: 'drop')
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    original_len = len(df)
    df_cleaned = df.copy()
    
    print(f"   Original records: {original_len}")
    
    # Remove rows with missing target variable (cannot be used for training)
    if target_col in df_cleaned.columns:
        missing_target = df_cleaned[target_col].isna().sum()
        if missing_target > 0:
            print(f"   Removing {missing_target} rows with missing {target_col}")
            df_cleaned = df_cleaned.dropna(subset=[target_col])
    
    # Handle missing values in feature columns
    if handle_missing == "drop":
        # Drop rows with any missing values in feature columns
        missing_features = df_cleaned.drop(columns=[target_col]).isna().sum().sum()
        if missing_features > 0:
            print(f"   Removing {missing_features} rows with missing feature values")
            df_cleaned = df_cleaned.dropna()
    elif handle_missing == "fill":
        # Fill missing numeric values with median
        numeric_cols = df_cleaned.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col != target_col and df_cleaned[col].isna().any():
                median_val = df_cleaned[col].median()
                df_cleaned[col].fillna(median_val, inplace=True)
                print(f"   Filled missing values in {col} with median: {median_val}")
        
        # Fill missing categorical values with mode
        categorical_cols = df_cleaned.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df_cleaned[col].isna().any():
                mode_val = df_cleaned[col].mode()[0] if not df_cleaned[col].mode().empty else "Unknown"
                df_cleaned[col].fillna(mode_val, inplace=True)
                print(f"   Filled missing values in {col} with mode: {mode_val}")
    
    # Remove duplicates
    if remove_duplicates:
        duplicates = df_cleaned.duplicated().sum()
        if duplicates > 0:
            print(f"   Removing {duplicates} duplicate records")
            df_cleaned = df_cleaned.drop_duplicates()
    
    final_len = len(df_cleaned)
    removed = original_len - final_len
    
    if removed > 0:
        print(f"   Removed {removed} records ({removed/original_len*100:.2f}%)")
        print(f"   Final records: {final_len}")
    else:
        print(f"   ✅ No records removed - data is clean")
    
    return df_cleaned


def validate_data(df, required_cols=None):
    """
    Validate that dataframe has required columns and no missing values in key columns.
    
    Args:
        df: DataFrame to validate
        required_cols: List of required column names
    
    Returns:
        bool: True if valid, raises ValueError if not
    """
    if required_cols:
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Check for missing values in key columns
    if 'Salary' in df.columns:
        if df['Salary'].isna().any():
            raise ValueError("Missing values found in 'Salary' column")
    
    return True


def merge_new_data(old_data_path, new_data_path, output_path=None, clean_new_data=True):
    """
    Merge new data with existing training data.
    Automatically cleans new data before merging to ensure data quality.
    
    Args:
        old_data_path: Path to existing training data
        new_data_path: Path to new data file
        output_path: Path to save merged data (default: overwrites old_data_path)
        clean_new_data: Whether to clean new data before merging (default: True)
    
    Returns:
        pd.DataFrame: Merged and cleaned dataframe
    """
    print("🔄 Merging new data with existing dataset...")
    
    # Load existing data
    old_df = load_data(old_data_path)
    print(f"   Existing data: {len(old_df)} records")
    
    # Load new data
    new_df = load_data(new_data_path)
    print(f"   New data: {len(new_df)} records")
    
    # Clean new data before merging (remove missing values and duplicates)
    if clean_new_data:
        print(f"\n🧹 Cleaning new data before merge...")
        new_df_original = len(new_df)
        new_df = clean_data(new_df, target_col="Salary", remove_duplicates=True, handle_missing="drop")
        print(f"   Cleaned new data: {len(new_df)} records (removed {new_df_original - len(new_df)} invalid records)")
    
    # Merge datasets
    merged_df = pd.concat([old_df, new_df], ignore_index=True)
    print(f"\n🔄 Merging datasets...")
    print(f"   Total after merge (before deduplication): {len(merged_df)} records")
    
    # Remove duplicates across entire merged dataset (cross-dataset duplicates)
    duplicates_before = len(merged_df)
    merged_df = merged_df.drop_duplicates()
    duplicates_removed = duplicates_before - len(merged_df)
    
    if duplicates_removed > 0:
        print(f"   ⚠️ Removed {duplicates_removed} duplicate records (already existed in existing data)")
    
    # Final validation: remove any remaining rows with missing target variable
    if "Salary" in merged_df.columns:
        missing_salary = merged_df["Salary"].isna().sum()
        if missing_salary > 0:
            print(f"   Removing {missing_salary} rows with missing Salary after merge")
            merged_df = merged_df.dropna(subset=["Salary"])
    
    # Save merged data
    if output_path is None:
        output_path = old_data_path
    
    merged_df.to_csv(output_path, index=False)
    print(f"\n✅ Merged data saved to: {output_path}")
    print(f"   Final records: {len(merged_df)}")
    print(f"   Records added: {len(merged_df) - len(old_df)}")
    
    return merged_df

