"""
train_model.py - OncoRisk ML

Trains multiple ML models on the processed and balanced dataset.

Models used and why:
    1. Logistic Regression - Simple linear baseline. If this works well,
       you don't need more complex models. Also provides interpretable
       feature coefficients.
    2. Random Forest - Ensemble of decision trees. Handles non-linear
       relationships well. Provides feature importance scores. Robust
       against overfitting due to bagging.
    3. XGBoost - Gradient-boosted trees. Typically the top performer on
       tabular/structured data. Has built-in regularization to prevent
       overfitting.
"""

# Implementation will be added in Phase 5.
# Functions planned:
#   - train_logistic_regression(X, y)
#   - train_random_forest(X, y)
#   - train_xgboost(X, y)
#   - train_all_models(X, y)
