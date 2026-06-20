from sqlalchemy.orm import Session
from backend.models.user import User
from backend.services.prediction_service import get_prediction_history
from backend.services.conversation_context_service import conversation_context_service

class ContextBuilderService:
    def build_context(self, db: Session, current_user: User) -> dict:
        """
        Builds structured context dictionary for the AI service.
        The AI service never directly queries database tables.
        """
        history = get_prediction_history(db, user_id=current_user.id, limit=10)
        
        # 1. Latest Prediction details
        latest_prediction = {}
        risk_level = "Unknown"
        top_risk_factors = []
        explanation_narrative = ""
        cancer_type = "Unknown"
        confidence_score = 0.0
        
        if history:
            latest_log = history[0]
            risk_level = latest_log.predicted_class
            confidence_score = latest_log.confidence_score
            explanation_narrative = latest_log.explanation_narrative
            cancer_type = latest_log.patient_data.get("Cancer_Type", "Unknown")
            
            # Extract contributing factors dynamically using explainer from predict.py
            import backend.api.predict as predict
            try:
                if predict.explainer is not None:
                    explanation = predict.explainer.explain_prediction(
                        patient_data=latest_log.patient_data,
                        prediction=latest_log.predicted_class,
                        confidence_score=latest_log.confidence_score
                    )
                    top_risk_factors = explanation.get("contributing_factors", [])
            except Exception as e:
                print(f"Context Builder Service Warning: explainer failed: {e}")
                
            latest_prediction = {
                "id": latest_log.id,
                "patient_data": latest_log.patient_data,
                "predicted_class": latest_log.predicted_class,
                "confidence_score": latest_log.confidence_score,
                "explanation_narrative": latest_log.explanation_narrative,
                "created_at": latest_log.created_at.isoformat()
            }

        # 2. Historical Runs
        history_list = []
        for log in history[1:]:
            history_list.append({
                "id": log.id,
                "patient_data": log.patient_data,
                "predicted_class": log.predicted_class,
                "confidence_score": log.confidence_score,
                "cancer_type": log.patient_data.get("Cancer_Type", "Unknown"),
                "created_at": log.created_at.isoformat()
            })

        # 3. Active Conversation context
        conversation = conversation_context_service.get_context(current_user.id)

        # 4. Platform Help Guidance
        allowed_platform_info = {
            "routes": {
                "Risk Assessment Page": "Navigate to the 'Risk Assessment' option from the main menu sidebar to complete user profiles.",
                "Prediction History Dashboard": "Open the 'Dashboard' section or 'Prediction History' option to view completed evaluations."
            },
            "concepts": {
                "Obesity Profile Index": "Indicates obesity-related contribution to overall risk calculation.",
                "Confidence Score": "Represents the model's calculated mathematical probability of the predicted risk category.",
                "SHAP values": "Identify individual mathematical contributions of lifestyle and clinical variables to the prediction."
            }
        }

        return {
            "user_id": current_user.id,
            "has_history": len(history) > 0,
            "risk_level": risk_level,
            "cancer_type": cancer_type,
            "confidence_score": confidence_score,
            "latest_prediction": latest_prediction,
            "top_risk_factors": top_risk_factors,
            "explanation_narrative": explanation_narrative,
            "history": history_list,
            "conversation": conversation,
            "allowed_platform_info": allowed_platform_info
        }

context_builder_service = ContextBuilderService()
