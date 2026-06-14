"""
main.py - OncoRisk ML

Main entry point for the ML pipeline. Orchestrates the full workflow:
    1. Load and validate data
    2. Preprocess
    3. Run EDA
    4. Apply SMOTE
    5. Train models
    6. Tune hyperparameters
    7. Evaluate models
    8. Save the best model

Each step calls functions from dedicated modules in src/.
"""

from src.data_ingestion import load_data, validate_data

# Pipeline configuration
RAW_DATA_PATH = "data/raw/cancer-risk-factors.csv"
PROCESSED_DATA_PATH = "data/processed/cleaned_data.csv"
MODEL_DIR = "models/"
VISUALS_DIR = "visuals/"


def run_pipeline():
    """Execute the full OncoRisk ML pipeline."""

    print("=" * 60)
    print("  OncoRisk ML - Cancer Risk Prediction Pipeline")
    print("=" * 60)

    # Step 1: Data Ingestion
    print("\n[Step 1] Loading dataset...")
    df = load_data(RAW_DATA_PATH)
    validate_data(df)

    # Steps 2-8 will be added as each module is implemented.
    print("\n[Pipeline] Steps 2-8 are under development.")
    print("[Pipeline] Run complete.\n")


if __name__ == "__main__":
    run_pipeline()
