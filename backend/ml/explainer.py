import os
import json
import pandas as pd

class OncoRiskExplainer:
    """
    Explains the model predictions by identifying key clinical and lifestyle
    risk factors from the patient profile and translating them to structured
    insights and plain-English narratives.
    """
    def __init__(self, evaluation_report_path: str = None):
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

    def explain_prediction(self, patient_data: dict, prediction: str, confidence_score: float) -> dict:
        """
        Generates explanation metrics and narrative for a single prediction.
        """
        contributions = []
        
        # 1. Define feature risk triggers and thresholds
        # Patient fields are numeric or binary
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
        
        # 2. Score each trigger based on feature importance and patient input
        for feature, val in patient_data.items():
            if feature in risk_rules:
                rule = risk_rules[feature]
                importance = self.feature_importances.get(feature, 0.01)
                
                # Check if patient value triggers the risk threshold
                is_risk = False
                if rule.get("reverse", False):
                    if val <= rule["threshold"]:
                        is_risk = True
                else:
                    if val >= rule["threshold"]:
                        is_risk = True
                        
                if is_risk:
                    # Calculate weight = feature importance * scale of risk
                    # For binary features, val is 1, scale is 1. For ordinal 0-10, scale is val/10
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
        
        # Sort contributions by impact score
        contributions = sorted(contributions, key=lambda x: x["impact_score"], reverse=True)
        
        # Keep top 4 contributing factors
        top_factors = contributions[:4]
        
        # Categorize impact levels based on impact score
        for factor in top_factors:
            score = factor["impact_score"]
            if score > 0.05:
                factor["impact_level"] = "High"
            elif score > 0.02:
                factor["impact_level"] = "Medium"
            else:
                factor["impact_level"] = "Low"
                
            # Clean up the output dict
            del factor["impact_score"]
            
        # 3. Generate plain English narrative
        narrative = self._generate_narrative(prediction, top_factors, patient_data)
        
        return {
            "prediction": prediction,
            "confidence_score": float(confidence_score),
            "contributing_factors": top_factors,
            "explanation_narrative": narrative
        }

    def _generate_narrative(self, prediction: str, top_factors: list, patient_data: dict) -> str:
        """
        Builds a clinical-style plain English explanation based on patient risk features.
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
