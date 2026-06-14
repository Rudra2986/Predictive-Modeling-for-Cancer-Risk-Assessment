"""
smote_handler.py - OncoRisk ML

Handles class imbalance using SMOTE (Synthetic Minority Oversampling Technique).

Why SMOTE?
    If the dataset has unequal class distribution (e.g., many more "Medium"
    risk patients than "High" or "Low"), the model may become biased toward
    the majority class. SMOTE generates synthetic samples for minority classes
    by interpolating between existing samples.

Why only on training data?
    Applying SMOTE to the test set would leak synthetic information into
    evaluation, giving unrealistically high scores. The test set must always
    reflect the real-world distribution.
"""

# Implementation will be added in Phase 4.
# Functions planned:
#   - apply_smote(X_train, y_train)
#   - compare_distribution(y_before, y_after)
