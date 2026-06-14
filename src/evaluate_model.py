"""
evaluate_model.py - OncoRisk ML

Model evaluation using multiple metrics and visualization.

Metrics used and why:
    - Accuracy: Overall correctness. Simple but can be misleading with
      imbalanced data.
    - Recall: How many actual positive cases the model catches. Critical in
      medical contexts -- missing a high-risk patient is worse than a
      false alarm.
    - F1-Score: Harmonic mean of precision and recall. Balances both concerns.
    - Confusion Matrix: Shows exactly where the model makes mistakes
      (which classes get confused with which).
"""

# Implementation will be added in Phase 7.
# Functions planned:
#   - evaluate_model(model, X_test, y_test)
#   - plot_confusion_matrix(model, X_test, y_test)
#   - compare_models(results_dict)
#   - plot_feature_importance(model, feature_names)
