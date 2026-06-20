from typing import List, Dict, Any
from backend.models.prediction_log import PredictionLog

class TrendAnalysisService:
    def analyze_trends(self, history: List[PredictionLog]) -> str:
        """
        Compares the latest two assessments for risk, confidence, SHAP contributors, 
        and lifestyle parameters. Enforces a minimum of 2 runs.
        """
        if len(history) < 2:
            return "You need to complete at least two risk assessments to perform a comparison and see trends over time."
            
        latest = history[0]
        previous = history[1]
        
        # Risk transition comparison
        latest_risk = latest.predicted_class
        prev_risk = previous.predicted_class
        
        if latest_risk != prev_risk:
            risk_trend = f"Your risk level transitioned from {prev_risk} to {latest_risk}."
        else:
            risk_trend = f"Your risk level remained consistent at {latest_risk}."

        # Confidence change
        latest_conf = latest.confidence_score * 100
        prev_conf = previous.confidence_score * 100
        conf_diff = latest_conf - prev_conf
        if abs(conf_diff) >= 0.5:
            direction = "increased" if conf_diff > 0 else "decreased"
            conf_trend = f"Model assessment certainty {direction} by {abs(conf_diff):.0f}% (from {prev_conf:.0f}% to {latest_conf:.0f}%)."
        else:
            conf_trend = f"Assessment certainty remained stable at {latest_conf:.0f}%."

        # Lifestyle input comparisons
        latest_data = latest.patient_data
        prev_data = previous.patient_data
        
        lifestyle_checks = {
            "Smoking": "Smoking index",
            "Alcohol_Use": "Alcohol consumption",
            "Obesity": "Obesity index",
            "BMI": "Body Mass Index (BMI)",
            "Physical_Activity": "Physical activity",
            "Diet_Red_Meat": "Red meat intake",
            "Diet_Salted_Processed": "Processed foods intake"
        }
        
        changes = []
        for key, name in lifestyle_checks.items():
            l_val = latest_data.get(key)
            p_val = prev_data.get(key)
            if l_val is not None and p_val is not None:
                diff = float(l_val) - float(p_val)
                if abs(diff) > 0.05:
                    if key == "BMI":
                        changes.append(f"{name} changed from {p_val:.1f} to {l_val:.1f}")
                    else:
                        changes.append(f"{name} changed from {int(p_val)} to {int(l_val)}")
                        
        if changes:
            lifestyle_trend = "Input changes detected: " + ", ".join(changes[:3]) + "."
        else:
            lifestyle_trend = "No significant lifestyle input parameter modifications detected between these runs."

        # Compile full narrative response
        narrative = (
            f"Comparison of your last two risk assessment logs:\n\n"
            f"1. **Risk Trend**: {risk_trend}\n"
            f"2. **Certainty Trend**: {conf_trend}\n"
            f"3. **Parameter Differences**: {lifestyle_trend}\n\n"
            f"Focus on improving modifiable behaviors to lower risk profiles over time."
        )
        return narrative

trend_analysis_service = TrendAnalysisService()
