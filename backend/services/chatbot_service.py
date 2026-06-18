import re
from sqlalchemy.orm import Session
from typing import Tuple, Dict, Any

from backend.models.chat_message import ChatMessage
from backend.models.user import User
from backend.services.prediction_service import get_prediction_history
from backend.services.guardrail_service import guardrail
from backend.services.recommendation_service import recommendation_engine
from backend.services.rate_limiter_service import rate_limiter

def build_patient_context(db: Session, current_user: User) -> dict:
    """
    Retrieves the user's latest prediction log and computes explainer contributing factors.
    Returns a structured context dictionary.
    """
    history = get_prediction_history(db, user_id=current_user.id, limit=1)
    if not history:
        return {}
        
    latest_log = history[0]
    
    # Retrieve the ML explainer dynamically from predict.py
    from backend.api.predict import explainer
    contributions = []
    
    try:
        if explainer is not None:
            explanation = explainer.explain_prediction(
                patient_data=latest_log.patient_data,
                prediction=latest_log.predicted_class,
                confidence_score=latest_log.confidence_score
            )
            contributions = explanation.get("contributing_factors", [])
    except Exception as e:
        print(f"Chatbot Context Builder Warning: Could not run explainer: {e}")
        
    return {
        "has_history": True,
        "age": latest_log.patient_data.get("Age", 0),
        "gender": "Male" if latest_log.patient_data.get("Gender") == 1 else "Female",
        "cancer_type": latest_log.patient_data.get("Cancer_Type", "Unknown"),
        "predicted_class": latest_log.predicted_class,
        "confidence_score": latest_log.confidence_score,
        "patient_data": latest_log.patient_data,
        "contributing_factors": contributions,
        "explanation_narrative": latest_log.explanation_narrative
    }

def generate_response(db: Session, current_user: User, message: str) -> Tuple[str, str]:
    """
    Orchestrates response generation.
    Enforces rate limits, validates safety guardrails, queries user contexts,
    and returns a tuple of (answer_text, confidence_level).
    
    This interface is pluggable and LLM-ready.
    """
    # 1. Enforce Rate Limit per user
    rate_limiter.check_rate_limit(current_user.id)
    
    # 2. Safety & Allow-list Validation
    is_safe, refusal_reason = guardrail.validate_message(message, current_user.id)
    if not is_safe:
        refusal_msg = (
            "I can only assist with health-related assessment guidance and interpretation "
            "of your OncoRisk results. I cannot assist with out-of-scope technical, programming, "
            "or administration commands."
        )
        return refusal_msg, "LOW"
        
    # 3. Retrieve Context
    context = build_patient_context(db, current_user)
    
    clean_msg = message.strip().lower()
    
    # 4. Handle Case: User has never taken an assessment
    if not context:
        is_about_self = any(x in clean_msg for x in ["my", "i", "result", "score", "prediction", "assessment", "improve", "history"])
        if is_about_self:
            no_history_msg = (
                "I couldn't find a previous assessment. Complete a risk assessment first so I "
                "can provide personalized guidance."
            )
            return no_history_msg, "LOW"
        else:
            # Let them query general medical facts even if no history
            general_health_msg = (
                "General Cancer Risk: Cancer risk is influenced by a combination of genetics "
                "(such as family history or specific mutations), environmental exposures, and lifestyle "
                "habits (such as tobacco use, diet, physical inactivity, and weight management). Keeping a healthy "
                "BMI, eating fresh produce, exercising weekly, and consulting primary care doctors for routine checkups "
                "are key preventive measures."
            )
            return general_health_msg, "MEDIUM"

    # 5. Intent routing & personalized text construction
    answer = ""
    confidence = "LOW"
    
    # Query type classification
    is_why_query = any(x in clean_msg for x in ["why", "score", "prediction", "result", "explain", "factors", "affected", "class"])
    is_improve_query = any(x in clean_msg for x in ["improve", "focus", "lower", "reduce", "lifestyle", "diet", "exercise", "smoking", "alcohol", "obesity", "bmi"])
    is_screening_query = any(x in clean_msg for x in ["screening", "test", "checkup", "mammogram", "colonoscopy", "exam", "detect"])
    
    if is_why_query:
        # HIGH_CONFIDENCE: Explaining user's actual prediction
        pred_class = context.get("predicted_class")
        conf_val = context.get("confidence_score", 1.0) * 100
        cancer_type = context.get("cancer_type", "Unknown")
        drivers = [f for f in context.get("contributing_factors", []) if f.get("shap_value", 0) > 0.005]
        
        driver_texts = []
        for drv in drivers[:3]:
            feat = drv.get("factor")
            val = drv.get("value")
            # format value cleanly
            if isinstance(val, float):
                val_str = f"{val:.1f}"
            else:
                val_str = str(val)
            driver_texts.append(f"**{feat}** (Value: {val_str})")
            
        drivers_joined = ", ".join(driver_texts)
        
        if drivers_joined:
            answer = (
                f"Based on your latest assessment for suspected **{cancer_type}** cancer, "
                f"your risk level is classified as **{pred_class}** (with a model confidence score of {conf_val:.0f}%). "
                f"The primary risk contributors identified by the machine learning explainer are {drivers_joined}. "
                "These factors had the highest positive mathematical impact on your risk score calculation."
            )
        else:
            narrative = context.get("explanation_narrative", "")
            answer = (
                f"Your latest risk assessment category is **{pred_class}** (confidence: {conf_val:.0f}%). "
                f"The clinical explanation generated is: \"{narrative}\""
            )
            
        confidence = "HIGH"
        
    elif is_improve_query:
        # HIGH_CONFIDENCE: Personalized lifestyle recommendations
        recs = recommendation_engine.generate_lifestyle_recommendations(context)
        if recs:
            bullet_recs = "\n".join([f"* {r}" for r in recs])
            answer = (
                "Based on your clinical variables and lifestyle indices from your last assessment, "
                "here are the primary areas you should focus on to lower your overall risk factors:\n\n"
                f"{bullet_recs}"
            )
        else:
            answer = (
                "Your latest assessment metrics reflect balanced lifestyle scores. To maintain this low-risk status, "
                "continue focusing on standard wellness guidelines, such as avoiding smoking, eating a rich "
                "fiber/antioxidant diet, and exercising regularly."
            )
        confidence = "HIGH"
        
    elif is_screening_query:
        # MEDIUM_CONFIDENCE: Educational screening information (non-prescriptive)
        screenings = recommendation_engine.generate_screening_guidelines(context)
        bullet_recs = "\n".join([f"* {r}" for r in screenings])
        answer = (
            "Common preventive screening methods associated with your demographic and risk profile: \n\n"
            f"{bullet_recs}\n\n"
            "Please note that screening tests should only be initiated after consulting with a qualified "
            "healthcare professional to select the correct timing and methods."
        )
        confidence = "MEDIUM"
        
    else:
        # LOW_CONFIDENCE fallback if we match allow-list keywords but query lacks context
        is_generic_health = any(x in clean_msg for x in ["cancer", "risk", "prevention", "healthy"])
        if is_generic_health:
            answer = (
                "Cancer risk is a multifactorial metric that depends on clinical markers, genetic mutations "
                "(like BRCA), environment (air pollution or occupational hazards), and lifestyle choices. "
                "Avoiding tobacco, limiting alcohol, exercising daily, maintaining a healthy BMI, and undergoing "
                "routine physical checks are standard methods to preserve long-term health."
            )
            confidence = "MEDIUM"
        else:
            # Anti-Hallucination block
            answer = (
                "I do not have enough information to answer that reliably. Please consult a qualified "
                "healthcare professional."
            )
            confidence = "LOW"

    # 6. Safety disclaimer force-append
    disclaimer = "\n\n*This information is educational only and does not replace professional medical advice.*"
    final_answer = answer + disclaimer
    
    # 7. Persist chat message in Postgres database
    try:
        chat_log = ChatMessage(
            user_id=current_user.id,
            question=message,
            answer=final_answer
        )
        db.add(chat_log)
        db.commit()
    except Exception as db_err:
        print(f"Chatbot Service Warning: Failed to persist chat log to database: {db_err}")
        
    return final_answer, confidence
