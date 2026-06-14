"""
tune_model.py - OncoRisk ML

Hyperparameter tuning using Optuna for Random Forest and XGBoost.

Why Optuna over GridSearch?
    - GridSearch tries every combination of parameters (slow, exponential growth).
    - Optuna uses Bayesian optimization -- it learns from previous trials to
      focus on the most promising parameter regions.
    - Much more efficient, especially when there are many hyperparameters.
    - Provides built-in visualization of optimization history.

Why not tune Logistic Regression?
    It serves as a simple baseline. Tuning it adds complexity without
    meaningful benefit for this project's learning goals.
"""

# Implementation will be added in Phase 6.
# Functions planned:
#   - tune_random_forest(X, y, n_trials)
#   - tune_xgboost(X, y, n_trials)
#   - get_best_model(study, model_type)
