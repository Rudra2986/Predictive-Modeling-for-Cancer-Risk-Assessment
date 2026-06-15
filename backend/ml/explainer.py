import os
import json
import joblib
import pandas as pd
import numpy as np
import shap

# Class index to label mappings
LABEL_TO_IDX = {"Low": 0, "Medium": 1, "High": 2}

class OncoRiskExplainer:
    """
    Explains the model predictions by identifying key clinical and lifestyle
    risk factors from the patient profile using SHAP (SHapley Additive exPlanations)
    and translating them to structured insights and plain-English narratives.
    """
    def __init__(self, model=None, preprocessor=None, evaluation_report_path: str = None):
        if evaluation_report_path is None:
            evaluation_report_path = os.path.join("reports", "model_evaluation.json")
            
        self.feature_importances = {}
        if os.path.exists(evaluation_report_path):
            try:
                with open(evaluation_report_path, "r") as f:
                    metrics = json.load(f)
                    self.feature_importances = metrics.get("feature_importances", {})
            except Exception as e:
                print(f"Warning: Could not load feature importances for explainer: {e}")
                
        # Default importances in case report load fails
        if not self.feature_importances:
            self.feature_importances = {
                "Air_Pollution": 0.15,
                "Family_History": 0.10,
                "Gender": 0.08,
                "Alcohol_Use": 0.07,
                "Diet_Salted_Processed": 0.06,
                "Smoking": 0.05,
                "H_Pylori_Infection": 0.05,
                "Occupational_Hazards": 0.04,
                "Diet_Red_Meat": 0.04,
                "Obesity": 0.04,
                "Physical_Activity": 0.02
            }

        # Save model and preprocessor references
        self.model = model
        self.preprocessor = preprocessor
        
        # Load from default disk paths if not provided
        MODEL_DIR = os.path.join("backend", "ml", "saved_models")
        MODEL_PATH = os.path.join(MODEL_DIR, "best_model.joblib")
        PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.joblib")
        
        if self.model is None and os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Explainer Warning: Failed to load model: {e}")
                
        if self.preprocessor is None and os.path.exists(PREPROCESSOR_PATH):
            try:
                self.preprocessor = joblib.load(PREPROCESSOR_PATH)
            except Exception as e:
                print(f"Explainer Warning: Failed to load preprocessor: {e}")
                
        # Initialize TreeExplainer for SHAP calculations
        self.shap_explainer = None
        if self.model is not None:
            try:
                # TreeExplainer works with XGBoost and scikit-learn tree models
                self.shap_explainer = shap.TreeExplainer(self.model)
                print("Explainer: Successfully initialized TreeExplainer for SHAP explainability.")
            except Exception as e:
                print(f"Explainer Warning: Could not initialize TreeExplainer: {e}. Falling back to default importance-based scaling.")

    def explain_prediction(self, patient_data: dict, prediction: str, confidence_score: float) -> dict:
        """
        Generates explanation metrics and narrative using dynamic SHAP values or falls back to rule-based logic.
        """
        # Attempt dynamic SHAP calculation
        if self.shap_explainer is not None and self.preprocessor is not None:
            try:
                patient_df = pd.DataFrame([patient_data])
                cols_to_drop = [c for c in ["Patient_ID", "Overall_Risk_Score", "Risk_Level"] if c in patient_df.columns]
                if cols_to_drop:
                    patient_df = patient_df.drop(columns=cols_to_drop)
                    
                X_processed = self.preprocessor.transform(patient_df)
                feature_names = self.preprocessor.get_feature_names()
                
                # Compute SHAP values
                shap_values = self.shap_explainer.shap_values(X_processed)
                c = LABEL_TO_IDX.get(prediction, 1) # target class index
                
                # Extract SHAP array for prediction class c
                if isinstance(shap_values, list):
                    # For multi-class lists
                    if len(shap_values) > c:
                        class_vals = shap_values[c][0]
                    else:
                        class_vals = shap_values[0][0]
                elif isinstance(shap_values, np.ndarray):
                    if len(shap_values.shape) == 3:
                        # shape: (n_samples, n_features, n_classes)
                        class_vals = shap_values[0, :, c]
                    elif len(shap_values.shape) == 2:
                        # shape: (n_samples, n_features)
                        class_vals = shap_values[0]
                    else:
                        class_vals = np.zeros(X_processed.shape[1])
                else:
                    # Explainer could return shap.Explanation object in newer versions
                    if hasattr(shap_values, "values"):
                        vals = shap_values.values
                        if len(vals.shape) == 3:
                            class_vals = vals[0, :, c]
                        elif len(vals.shape) == 2:
                            class_vals = vals[0]
                        else:
                            class_vals = np.zeros(X_processed.shape[1])
                    else:
                        class_vals = np.zeros(X_processed.shape[1])
                
                # Define feature categories
                categories = {
                    "Age": "Lifestyle",
                    "Gender": "Clinical",
                    "Smoking": "Lifestyle",
                    "Alcohol_Use": "Lifestyle",
                    "Obesity": "Lifestyle",
                    "Family_History": "Clinical",
                    "Diet_Red_Meat": "Lifestyle",
                    "Diet_Salted_Processed": "Lifestyle",
                    "Fruit_Veg_Intake": "Lifestyle",
                    "Physical_Activity": "Lifestyle",
                    "Air_Pollution": "Environmental",
                    "Occupational_Hazards": "Environmental",
                    "BRCA_Mutation": "Clinical",
                    "H_Pylori_Infection": "Clinical",
                    "Calcium_Intake": "Lifestyle",
                    "BMI": "Lifestyle",
                    "Physical_Activity_Level": "Lifestyle"
                }
                
                contributions = []
                for idx, feat_name in enumerate(feature_names):
                    shap_val = float(class_vals[idx])
                    
                    # Skip columns with negligible SHAP values to reduce noise
                    if abs(shap_val) < 1e-5:
                        continue
                        
                    # Find category and actual patient value
                    if feat_name.startswith("Cancer_Type_"):
                        category = "Clinical"
                        actual_val = 1.0 if patient_data.get("Cancer_Type") == feat_name.split("_")[-1] else 0.0
                    else:
                        category = categories.get(feat_name, "Clinical")
                        actual_val = float(patient_data.get(feat_name, 0.0))
                        
                    readable_feat = self._get_readable_name(feat_name)
                    
                    contributions.append({
                        "factor": readable_feat,
                        "category": category,
                        "value": actual_val,
                        "shap_value": shap_val
                    })
                    
                # Sort contributions by absolute SHAP value to find most impactful ones
                sorted_contribs = sorted(contributions, key=lambda x: abs(x["shap_value"]), reverse=True)
                
                # Keep top 5 contributing factors
                top_factors = sorted_contribs[:5]
                
                # Label impact level (High, Medium, Low) and impact direction (Risk vs Protective)
                max_abs_shap = max([abs(x["shap_value"]) for x in top_factors]) if top_factors else 1.0
                
                for factor in top_factors:
                    val = factor["shap_value"]
                    factor["impact_level"] = "High" if abs(val) > 0.4 * max_abs_shap else "Medium" if abs(val) > 0.15 * max_abs_shap else "Low"
                    factor["impact"] = factor["impact_level"]
                    
                # Generate dynamic explanation narrative from SHAP risk factors and protective factors
                narrative = self._generate_shap_narrative(prediction, top_factors, patient_data)
                
                return {
                    "prediction": prediction,
                    "confidence_score": float(confidence_score),
                    "contributing_factors": top_factors,
                    "explanation_narrative": narrative
                }
                
            except Exception as e:
                print(f"Explainer Warning: Dynamic SHAP calculation failed: {e}. Falling back to default explainer.")
        
        # --- Fallback Option: Static Rule-based Engine ---
        contributions = []
        risk_rules = {
            "Smoking": {"threshold": 5, "desc": "High smoking index", "category": "Lifestyle"},
            "Alcohol_Use": {"threshold": 5, "desc": "High alcohol consumption", "category": "Lifestyle"},
            "Obesity": {"threshold": 5, "desc": "High obesity index", "category": "Lifestyle"},
            "Family_History": {"threshold": 1, "desc": "Family history of cancer", "category": "Clinical"},
            "Diet_Red_Meat": {"threshold": 5, "desc": "Frequent red meat intake", "category": "Lifestyle"},
            "Diet_Salted_Processed": {"threshold": 5, "desc": "High intake of processed and salted foods", "category": "Lifestyle"},
            "Fruit_Veg_Intake": {"threshold": 4, "desc": "Low fruit and vegetable intake", "category": "Lifestyle", "reverse": True},
            "Physical_Activity": {"threshold": 4, "desc": "Sedentary lifestyle (low physical activity)", "category": "Lifestyle", "reverse": True},
            "Air_Pollution": {"threshold": 5, "desc": "High exposure to environmental air pollution", "category": "Environmental"},
            "Occupational_Hazards": {"threshold": 5, "desc": "High exposure to occupational hazards", "category": "Environmental"},
            "BRCA_Mutation": {"threshold": 1, "desc": "BRCA genetic mutation present", "category": "Clinical"},
            "H_Pylori_Infection": {"threshold": 1, "desc": "Active H. Pylori bacterial infection", "category": "Clinical"},
            "Calcium_Intake": {"threshold": 4, "desc": "Insufficient dietary calcium intake", "category": "Lifestyle", "reverse": True},
            "BMI": {"threshold": 25.0, "desc": "Elevated BMI (overweight or obese)", "category": "Lifestyle"},
            "Physical_Activity_Level": {"threshold": 4, "desc": "Low active exercise level", "category": "Lifestyle", "reverse": True}
        }
        
        for feature, val in patient_data.items():
            if feature in risk_rules:
                rule = risk_rules[feature]
                importance = self.feature_importances.get(feature, 0.01)
                
                is_risk = False
                if rule.get("reverse", False):
                    if val <= rule["threshold"]:
                        is_risk = True
                else:
                    if val >= rule["threshold"]:
                        is_risk = True
                        
                if is_risk:
                    scale = 1.0
                    if not rule.get("reverse", False) and isinstance(val, (int, float)) and val > 0 and feature != "BMI":
                        scale = val / 10.0
                        
                    impact_score = importance * scale
                    contributions.append({
                        "factor": rule["desc"],
                        "category": rule["category"],
                        "value": val,
                        "impact_score": impact_score
                    })
        
        contributions = sorted(contributions, key=lambda x: x["impact_score"], reverse=True)
        top_factors = contributions[:4]
        
        for factor in top_factors:
            score = factor["impact_score"]
            if score > 0.05:
                factor["impact_level"] = "High"
            elif score > 0.02:
                factor["impact_level"] = "Medium"
            else:
                factor["impact_level"] = "Low"
                
            factor["impact"] = factor["impact_level"]
            factor["shap_value"] = score # mock shap value for frontend schema compatibility
            del factor["impact_score"]
            
        narrative = self._generate_narrative(prediction, top_factors, patient_data)
        
        return {
            "prediction": prediction,
            "confidence_score": float(confidence_score),
            "contributing_factors": top_factors,
            "explanation_narrative": narrative
        }

    def _get_readable_name(self, feature_name: str) -> str:
        mapping = {
            "Age": "Patient Age",
            "Gender": "Gender Profile",
            "Smoking": "Smoking Habits",
            "Alcohol_Use": "Alcohol Consumption",
            "Obesity": "Obesity Profile",
            "Family_History": "Family Cancer History",
            "Diet_Red_Meat": "Red Meat Intake",
            "Diet_Salted_Processed": "Processed/Salted Food Intake",
            "Fruit_Veg_Intake": "Fruit & Vegetable Intake",
            "Physical_Activity": "Physical Activity Frequency",
            "Air_Pollution": "Air Pollution Exposure",
            "Occupational_Hazards": "Occupational Hazards",
            "BRCA_Mutation": "BRCA Mutation",
            "H_Pylori_Infection": "H. Pylori Infection",
            "Calcium_Intake": "Calcium Intake",
            "BMI": "Body Mass Index (BMI)",
            "Physical_Activity_Level": "Active Exercise Level"
        }
        if feature_name in mapping:
            return mapping[feature_name]
        if feature_name.startswith("Cancer_Type_"):
            cancer_type = feature_name.split("_")[-1]
            return f"Suspected Cancer: {cancer_type}"
        return feature_name.replace("_", " ")

    def _generate_shap_narrative(self, prediction: str, top_factors: list, patient_data: dict) -> str:
        """
        Builds a clinical narrative using SHAP values: positive SHAP indicates risk drivers,
        negative SHAP indicates protective factors.
        """
        risk_drivers = [f for f in top_factors if f["shap_value"] > 0.01]
        protective_factors = [f for f in top_factors if f["shap_value"] < -0.01]
        
        risk_drivers = sorted(risk_drivers, key=lambda x: abs(x["shap_value"]), reverse=True)
        protective_factors = sorted(protective_factors, key=lambda x: abs(x["shap_value"]), reverse=True)
        
        if prediction == "Low":
            if protective_factors:
                protect_str = ", supported by protective factors such as " + " and ".join([f["factor"].lower() for f in protective_factors[:2]])
            else:
                protect_str = ""
            return f"The assessment indicates a low cancer risk profile{protect_str}. No critical genetic indicators or highly elevated lifestyle threats were detected."
            
        elif prediction == "Medium":
            risk_parts = []
            if risk_drivers:
                risk_parts.append("primarily driven by " + " and ".join([f["factor"].lower() for f in risk_drivers[:2]]))
            if protective_factors:
                risk_parts.append("partially mitigated by protective markers like " + " and ".join([f["factor"].lower() for f in protective_factors[:2]]))
                
            drivers = ", and ".join(risk_parts) if risk_parts else "minor elevations in lifestyle or clinical risk criteria"
            return f"A moderate risk profile is indicated, {drivers}. Recommended actions include regular screenings and preventative lifestyle adjustments."
            
        else: # High
            risk_str = " and ".join([f["factor"].lower() for f in risk_drivers[:2]]) if risk_drivers else "critical clinical indicators"
            protect_str = ""
            if protective_factors:
                protect_str = f" despite minor protective contributions from {protective_factors[0]['factor'].lower()}"
                
            return f"A high cancer risk score has been generated, heavily influenced by {risk_str}{protect_str}. Immediate medical consultation and diagnostic screenings are strongly advised to evaluate these risk factors."

    def _generate_narrative(self, prediction: str, top_factors: list, patient_data: dict) -> str:
        """
        Fallback narrative builder.
        """
        if prediction == "Low":
            if not top_factors:
                return "The patient exhibits a healthy profile with balanced lifestyle choices and no critical clinical genetic markers."
            factor_list = ", ".join([f["factor"].lower() for f in top_factors[:2]])
            return f"The overall risk is low. Although minor factors such as {factor_list} were detected, they do not present a combined clinical threat."
            
        elif prediction == "Medium":
            if not top_factors:
                return "The overall risk profile is moderate, suggesting minor elevation in lifestyle or clinical risk criteria that warrant monitoring."
            
            high_factors = [f for f in top_factors if f.get("impact_level") in ["High", "Medium"]]
            if high_factors:
                factor_str = " and ".join([f["factor"].lower() for f in high_factors[:2]])
                return f"The assessment suggests a moderate cancer risk profile, primarily driven by {factor_str}. Moderate lifestyle adjustments or periodic clinical screenings are recommended."
            else:
                factor_str = top_factors[0]["factor"].lower()
                return f"A moderate risk is indicated, influenced by {factor_str}. Routine preventative care and health monitoring are advised."
                
        else: # High Risk
            if not top_factors:
                return "The patient profile exhibits several elevated risk markers across multiple diagnostic vectors. Immediate clinical consultation is advised."
            
            clinical_factors = [f for f in top_factors if f["category"] == "Clinical"]
            lifestyle_factors = [f for f in top_factors if f["category"] == "Lifestyle"]
            environmental_factors = [f for f in top_factors if f["category"] == "Environmental"]
            
            segments = []
            if clinical_factors:
                segments.append(f"significant clinical flags including {clinical_factors[0]['factor'].lower()}")
            if lifestyle_factors:
                segments.append(f"lifestyle behaviors such as {lifestyle_factors[0]['factor'].lower()}")
            if environmental_factors:
                segments.append(f"environmental exposures, notably {environmental_factors[0]['factor'].lower()}")
                
            if not segments:
                segments.append(f"critical contributions from {top_factors[0]['factor'].lower()}")
                
            drivers = ", compounded by ".join(segments)
            return f"A high risk score has been generated due to {drivers}. It is highly recommended that this patient undergoes detailed clinical diagnostic screening and consults with a medical professional."
