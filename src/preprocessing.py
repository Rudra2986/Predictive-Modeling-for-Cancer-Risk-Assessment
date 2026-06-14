"""
preprocessing.py - OncoRisk ML

Handles data cleaning, encoding, scaling, and train/test splitting.
All transformations applied to the raw data before model training happen here.

Why preprocessing is separated from data ingestion:
    Data ingestion deals with WHERE the data comes from.
    Preprocessing deals with HOW the data is transformed.
    Keeping them separate means you can swap data sources without
    rewriting your cleaning logic.
"""

# Implementation will be added in Phase 2.
# Functions planned:
#   - drop_unnecessary_columns(df)
#   - encode_categorical(df)
#   - scale_features(df, target_col)
#   - split_data(df, target_col)
