import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import optuna

# Import local preprocessor
from backend.ml.preprocessor import OncoRiskPreprocessor
from backend.services.retrain_service import retrain_service

# Disable Optuna log spam
optuna.logging.set_verbosity(optuna.logging.WARNING)

# Mappings for target classes
LABEL_TO_IDX = {"Low": 0, "Medium": 1, "High": 2}
IDX_TO_LABEL = {0: "Low", 1: "Medium", 2: "High"}

def load_data(file_path: str):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dataset file not found at: {file_path}")
    return pd.read_csv(file_path)

def build_and_train(n_trials: int = 15):
    try:
        retrain_service.reset(n_trials)
        retrain_service.current_step = "Loading patient data"
        retrain_service.log("Step 1: Loading patient risk assessment data...")
        dataset_path = os.path.join("datasets", "raw", "cancer-risk-factors.csv")
        df = load_data(dataset_path)
        
        # 2. Prevent target leakage: Drop Patient_ID and Overall_Risk_Score
        # Patient_ID has no predictive power
        # Overall_Risk_Score is directly mapped to Risk_Level classes
        X = df.drop(columns=["Patient_ID", "Overall_Risk_Score", "Risk_Level"])
        y = df["Risk_Level"].map(LABEL_TO_IDX)
        
        # Check data balance
        retrain_service.log(f"Original class distribution: {df['Risk_Level'].value_counts().to_dict()}")
        
        # 3. Train-test split
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 4. Fit Preprocessing Pipeline
        retrain_service.current_step = "Fitting preprocessor"
        retrain_service.log("Step 2: Fitting feature preprocessor...")
        preprocessor = OncoRiskPreprocessor()
        X_train = preprocessor.fit_transform(X_train_raw)
        X_test = preprocessor.transform(X_test_raw)
        
        # 5. Handle Imbalance using SMOTE
        retrain_service.current_step = "Balancing classes"
        retrain_service.log("Step 3: Balancing classes via SMOTE...")
        smote = SMOTE(random_state=42)
        X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)
        retrain_service.log(f"Balanced class distribution: {pd.Series(y_train_balanced).value_counts().to_dict()}")
        
        # 6. Fit Baseline Logistic Regression
        retrain_service.current_step = "Baseline training"
        retrain_service.log("Step 4: Training baseline Logistic Regression...")
        lr_baseline = LogisticRegression(max_iter=1000, random_state=42)
        lr_baseline.fit(X_train_balanced, y_train_balanced)
        y_pred_lr = lr_baseline.predict(X_test)
        lr_f1 = f1_score(y_test, y_pred_lr, average="weighted")
        retrain_service.log(f"Logistic Regression Baseline Weighted F1: {lr_f1:.4f}")
        
        # 7. Optimize Random Forest using Optuna
        retrain_service.current_step = "Optimizing Random Forest"
        retrain_service.log("Step 5: Optimizing Random Forest Classifier...")
        
        def rf_objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 200),
                "max_depth": trial.suggest_int("max_depth", 5, 20),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
                "random_state": 42
            }
            model = RandomForestClassifier(**params)
            model.fit(X_train_balanced, y_train_balanced)
            preds = model.predict(X_test)
            f1 = f1_score(y_test, preds, average="weighted")
            
            # Log progress
            trial_num = trial.number
            retrain_service.update_trial(trial_num, "Random Forest", f1)
            return f1
            
        rf_study = optuna.create_study(direction="maximize")
        rf_study.optimize(rf_objective, n_trials=n_trials)
        best_rf_params = rf_study.best_params
        retrain_service.log(f"Best Random Forest F1: {rf_study.best_value:.4f}")
        
        # Train Best RF
        best_rf = RandomForestClassifier(**best_rf_params, random_state=42)
        best_rf.fit(X_train_balanced, y_train_balanced)
        
        # 8. Optimize XGBoost using Optuna
        retrain_service.current_step = "Optimizing XGBoost"
        retrain_service.log("Step 6: Optimizing XGBoost Classifier...")
        
        def xgb_objective(trial):
            params = {
                "n_estimators": trial.suggest_int("n_estimators", 50, 200),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.6, 1.0),
                "random_state": 42,
                "eval_metric": "mlogloss"
            }
            model = xgb.XGBClassifier(**params)
            model.fit(X_train_balanced, y_train_balanced)
            preds = model.predict(X_test)
            f1 = f1_score(y_test, preds, average="weighted")
            
            # Log progress
            trial_num = n_trials + trial.number
            retrain_service.update_trial(trial_num, "XGBoost", f1)
            return f1
            
        xgb_study = optuna.create_study(direction="maximize")
        xgb_study.optimize(xgb_objective, n_trials=n_trials)
        best_xgb_params = xgb_study.best_params
        retrain_service.log(f"Best XGBoost F1: {xgb_study.best_value:.4f}")
        
        # Train Best XGBoost
        best_xgb = xgb.XGBClassifier(**best_xgb_params, random_state=42)
        best_xgb.fit(X_train_balanced, y_train_balanced)
        
        # 9. Model Selection
        retrain_service.current_step = "Selecting best model"
        models = {
            "Logistic Regression": (lr_baseline, f1_score(y_test, y_pred_lr, average="weighted")),
            "Random Forest": (best_rf, rf_study.best_value),
            "XGBoost": (best_xgb, xgb_study.best_value)
        }
        
        best_model_name = max(models, key=lambda k: models[k][1])
        best_model, best_f1 = models[best_model_name]
        retrain_service.log(f"\nWinner Model Selected: {best_model_name} with F1-score {best_f1:.4f}")
        
        # 10. Generate evaluation metrics for the winning model
        y_pred = best_model.predict(X_test)
        report_dict = classification_report(y_test, y_pred, output_dict=True, target_names=["Low", "Medium", "High"])
        cm = confusion_matrix(y_test, y_pred).tolist()
        
        # Extract feature importance if available
        feature_names = preprocessor.get_feature_names()
        feature_importance_dict = {}
        if hasattr(best_model, "feature_importances_"):
            importances = best_model.feature_importances_
            feature_importance_dict = {
                name: float(imp) for name, imp in zip(feature_names, importances)
            }
            # Sort importances
            feature_importance_dict = dict(sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True))
        elif hasattr(best_model, "coef_"):
            # For Logistic Regression, use average magnitude of coefficients across classes
            coefs = np.mean(np.abs(best_model.coef_), axis=0)
            feature_importance_dict = {
                name: float(coef) for name, coef in zip(feature_names, coefs)
            }
            feature_importance_dict = dict(sorted(feature_importance_dict.items(), key=lambda item: item[1], reverse=True))
            
        metrics = {
            "model_name": best_model_name,
            "weighted_f1": best_f1,
            "accuracy": accuracy_score(y_test, y_pred),
            "classification_report": report_dict,
            "confusion_matrix": cm,
            "feature_importances": feature_importance_dict
        }
        
        # Save reports
        os.makedirs("reports", exist_ok=True)
        with open(os.path.join("reports", "model_evaluation.json"), "w") as f:
            json.dump(metrics, f, indent=4)
        retrain_service.log("Saved evaluation report to reports/model_evaluation.json")
        
        # Save best model and preprocessor
        os.makedirs(os.path.join("backend", "ml", "saved_models"), exist_ok=True)
        joblib.dump(best_model, os.path.join("backend", "ml", "saved_models", "best_model.joblib"))
        joblib.dump(preprocessor, os.path.join("backend", "ml", "saved_models", "preprocessor.joblib"))
        retrain_service.log("Saved best model and preprocessor to backend/ml/saved_models/")
        
        # Notify retrain_service of completion
        retrain_service.complete(best_model_name, best_f1)
        
    except Exception as e:
        retrain_service.fail(str(e))
        raise e

if __name__ == "__main__":
    build_and_train()

