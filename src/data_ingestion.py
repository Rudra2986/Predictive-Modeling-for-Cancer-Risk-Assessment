"""
data_ingestion.py - OncoRisk ML

Handles loading raw data from CSV files and performing initial validation.
This module is the entry point for all data flowing into the pipeline.

Why a separate module?
    Separating data loading from preprocessing follows the single-responsibility
    principle. If the data source changes (CSV to database, API, etc.), only
    this file needs updating. The rest of the pipeline stays untouched.
"""

import pandas as pd
import os


def load_data(filepath):
    """Load a CSV file and return a pandas DataFrame.

    Args:
        filepath (str): Path to the CSV file.

    Returns:
        pd.DataFrame: Loaded dataset.

    Raises:
        FileNotFoundError: If the file does not exist at the given path.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset not found at: {filepath}")

    df = pd.read_csv(filepath)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def validate_data(df):
    """Run basic validation checks on the loaded DataFrame.

    Checks for:
        - Missing values per column
        - Duplicate rows
        - Data types summary

    Args:
        df (pd.DataFrame): The dataset to validate.

    Returns:
        dict: Summary of validation results.
    """
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicate_rows": df.duplicated().sum(),
        "dtypes": df.dtypes.astype(str).to_dict()
    }

    print(f"Total rows: {summary['total_rows']}")
    print(f"Total columns: {summary['total_columns']}")
    print(f"Duplicate rows: {summary['duplicate_rows']}")

    missing = df.isnull().sum()
    if missing.any():
        print("Columns with missing values:")
        print(missing[missing > 0])
    else:
        print("No missing values found.")

    return summary


def save_processed_data(df, filepath):
    """Save a processed DataFrame to CSV.

    Args:
        df (pd.DataFrame): Processed dataset.
        filepath (str): Destination path for the CSV file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"Processed data saved to: {filepath}")


def get_data_summary(df, target_col="Risk_Level"):
    """Print a quick summary of the dataset including target distribution.

    Useful for a fast sanity check at any stage of the pipeline.

    Args:
        df (pd.DataFrame): The dataset.
        target_col (str): Name of the target column.
    """
    print(f"\nDataset shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")

    if target_col in df.columns:
        print(f"\nTarget column '{target_col}' distribution:")
        counts = df[target_col].value_counts()
        for label, count in counts.items():
            pct = (count / len(df)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
    else:
        print(f"\nTarget column '{target_col}' not found in dataset.")

