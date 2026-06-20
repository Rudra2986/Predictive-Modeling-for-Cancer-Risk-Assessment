import re
from sqlalchemy.orm import Session
from typing import Tuple, Dict, Any

from backend.models.chat_message import ChatMessage
from backend.models.user import User
from backend.services.prediction_service import get_prediction_history
from backend.services.guardrail_service import guardrail
from backend.services.recommendation_service import recommendation_engine
from backend.services.rate_limiter_service import rate_limiter
from backend.services.platform_help_service import platform_help_service
from backend.services.assessment_guidance_service import assessment_guidance_service
from backend.services.conversation_context_service import conversation_context_service

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

def clear_user_chatbot_context(user_id: int) -> None:
    """
    Clears the active conversation context for the specified user.
    """
    conversation_context_service.clear_context(user_id)

def generate_response(db: Session, current_user: User, message: str) -> Tuple[str, str]:
    """
    Orchestrates response generation.
    Enforces rate limits, classifies the query, processes follow-up logic or standard intents,
    and returns a tuple of (answer_text, confidence_level).
    """
    # 1. Enforce Rate Limit per user
    rate_limiter.check_rate_limit(current_user.id)
    
    # Standard refusal message for security sensitive and out-of-scope questions
    refusal_msg = (
        "I can only assist with health-related assessment guidance and interpretation "
        "of your OncoRisk results. I cannot assist with out-of-scope technical, programming, "
        "or administration commands."
    )

    # 2. Safety & Allow-list Validation Classify
    category, refusal_reason = guardrail.classify_message(message, current_user.id)
    if category == guardrail.PROMPT_INJECTION:
        return "I cannot assist with requests that attempt to bypass system safety or access restricted information.", "LOW"
    elif category == guardrail.SECURITY_SENSITIVE:
        return refusal_msg, "LOW"
        
    # 3. Check for Follow-Up Queries (Simplify or Anything Else) using conversation context service
    clean_msg = message.strip().lower()
    is_simplify = any(x in clean_msg for x in ["simpler words", "simplify", "simple words", "simple terms", "simpler", "simple"])
    is_anything_else = any(x in clean_msg for x in ["anything else", "what else", "tell me more", "more details", "go on"])
    
    history = conversation_context_service.get_context(current_user.id)
    
    answer = ""
    confidence = "LOW"
    intent = None
    
    if is_simplify or is_anything_else:
        if not history:
            if is_simplify:
                answer = "I do not have a previous response to simplify."
                confidence = "LOW"
                intent = "SIMPLIFY"
            else:
                answer = (
                    "To learn more, you can explore the other sections of the dashboard or consult a "
                    "healthcare provider for personalized medical advice."
                )
                confidence = "MEDIUM"
                intent = "ANYTHING_ELSE"
        else:
            if is_simplify:
                last_bot_msg = None
                last_bot_conf = "MEDIUM"
                for entry in reversed(history):
                    if entry["role"] == "assistant":
                        last_bot_msg = entry["message"]
                        last_bot_conf = entry.get("confidence", "MEDIUM")
                        break
                
                if last_bot_msg:
                    # Strip safety disclaimer
                    disclaimer = "\n\n*This information is educational only and does not replace professional medical advice.*"
                    clean_text = last_bot_msg.replace(disclaimer, "").strip()
                    
                    # Simplify terms
                    clean_text = clean_text.replace("machine learning explainer", "analysis")
                    clean_text = clean_text.replace("SHAP (SHapley Additive exPlanations) values", "risk factors impact")
                    clean_text = re.sub(r"with a model confidence score of \d+%", "with high certainty", clean_text)
                    clean_text = re.sub(r"\*\*([^*]+)\*\* \(Value: [^)]+\)", r"\1 level", clean_text)
                    
                    answer = f"Simply put: {clean_text}"
                    confidence = last_bot_conf
                    intent = "SIMPLIFY"
                else:
                    answer = "I do not have a previous response to simplify."
                    confidence = "LOW"
                    intent = "SIMPLIFY"
                    
            elif is_anything_else:
                # Find the last assistant intent
                last_intent = None
                for entry in reversed(history):
                    if entry["role"] == "assistant" and entry.get("intent"):
                        last_intent = entry["intent"]
                        break
                
                if last_intent == "MEDICAL_LIFESTYLE":
                    answer = (
                        "In addition to the recommendations above, you should focus on general wellness habits: "
                        "manage stress levels, get 7-8 hours of sleep nightly, stay hydrated, and maintain consistent regular exercise."
                    )
                    confidence = "HIGH"
                elif last_intent == "MEDICAL_SCREENING":
                    answer = (
                        "Additionally, ensure you schedule an annual checkup with your primary physician, "
                        "keep track of any unusual physical symptoms, and review your immunization records."
                    )
                    confidence = "MEDIUM"
                elif last_intent == "MEDICAL_WHY_RISK":
                    answer = (
                        "Besides the factors mentioned, you can review your full profile metrics on the dashboard "
                        "to see how other variables (such as environmental or dietary habits) might influence your health trends."
                    )
                    confidence = "HIGH"
                else:
                    answer = (
                        "To learn more, you can explore the other sections of the dashboard or consult a "
                        "healthcare provider for personalized medical advice."
                    )
                    confidence = "MEDIUM"
                intent = "ANYTHING_ELSE"
            
    # 4. Standard routing based on intent category
    elif category == guardrail.PLATFORM_HELP:
        answer = platform_help_service.get_help_response(message)
        confidence = "MEDIUM"
        intent = "PLATFORM_HELP"
        
    elif category == guardrail.ASSESSMENT_GUIDANCE:
        answer = assessment_guidance_service.get_guidance_response(message)
        confidence = "MEDIUM"
        intent = "ASSESSMENT_GUIDANCE"
        
    elif category == guardrail.MEDICAL_QUERY:
        # Retrieve Patient Context
        context = build_patient_context(db, current_user)
        
        # Handle Case: User has never taken an assessment
        if not context:
            words = set(re.findall(r"\b\w+\b", clean_msg))
            is_about_self = any(x in words for x in ["my", "i", "me", "myself"]) or any(x in clean_msg for x in ["result", "score", "prediction", "assessment", "improve", "history"])
            if is_about_self:
                answer = (
                    "I couldn't find a previous assessment. Complete a risk assessment first so I "
                    "can provide personalized guidance."
                )
                confidence = "LOW"
                intent = "MEDICAL_NO_HISTORY"
            else:
                # General health guidelines
                answer = (
                    "General Cancer Risk: Cancer risk is influenced by a combination of genetics "
                    "(such as family history or specific mutations), environmental exposures, and lifestyle "
                    "habits (such as tobacco use, diet, physical inactivity, and weight management). Keeping a healthy "
                    "BMI, eating fresh produce, exercising weekly, and consulting primary care doctors for routine checkups "
                    "are key preventive measures."
                )
                confidence = "MEDIUM"
                intent = "MEDICAL_GENERIC"
        else:
            # Query type classification
            is_why_query = any(x in clean_msg for x in ["why", "score", "prediction", "result", "explain", "factors", "affected", "class", "my risk", "what is my risk"])
            is_improve_query = any(x in clean_msg for x in ["improve", "focus", "lower", "reduce", "lifestyle", "diet", "exercise", "smoking", "alcohol", "obesity", "bmi"])
            is_screening_query = any(x in clean_msg for x in ["screening", "test", "checkup", "mammogram", "colonoscopy", "exam", "detect"])
            
            if is_why_query:
                pred_class = context.get("predicted_class")
                conf_val = context.get("confidence_score", 1.0) * 100
                cancer_type = context.get("cancer_type", "Unknown")
                drivers = [f for f in context.get("contributing_factors", []) if f.get("shap_value", 0) > 0.005]
                
                driver_texts = []
                for drv in drivers[:3]:
                    feat = drv.get("factor")
                    val = drv.get("value")
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
                intent = "MEDICAL_WHY_RISK"
                
            elif is_improve_query:
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
                intent = "MEDICAL_LIFESTYLE"
                
            elif is_screening_query:
                screenings = recommendation_engine.generate_screening_guidelines(context)
                bullet_recs = "\n".join([f"* {r}" for r in screenings])
                answer = (
                    "Common preventive screening methods associated with your demographic and risk profile: \n\n"
                    f"{bullet_recs}\n\n"
                    "Please note that screening tests should only be initiated after consulting with a qualified "
                    "healthcare professional to select the correct timing and methods."
                )
                confidence = "MEDIUM"
                intent = "MEDICAL_SCREENING"
                
            else:
                is_generic_health = any(x in clean_msg for x in ["cancer", "risk", "prevention", "healthy"])
                if is_generic_health:
                    answer = (
                        "Cancer risk is a multifactorial metric that depends on clinical markers, genetic mutations "
                        "(like BRCA), environment (air pollution or occupational hazards), and lifestyle choices. "
                        "Avoiding tobacco, limiting alcohol, exercising daily, maintaining a healthy BMI, and undergoing "
                        "routine physical checks are standard methods to preserve long-term health."
                    )
                    confidence = "MEDIUM"
                    intent = "MEDICAL_GENERIC"
                else:
                    answer = (
                        "I do not have enough information to answer that reliably. Please consult a qualified "
                        "healthcare professional."
                    )
                    confidence = "LOW"
                    intent = "MEDICAL_FALLBACK"
    else:
        # OUT_OF_SCOPE category fallback
        return refusal_msg, "LOW"

    # 5. Safety disclaimer force-append
    final_answer = answer
    
    # 6. Append messages to conversation context service
    conversation_context_service.append_message(
        user_id=current_user.id,
        role="user",
        message=message
    )
    conversation_context_service.append_message(
        user_id=current_user.id,
        role="assistant",
        message=final_answer,
        intent=intent,
        confidence=confidence
    )
    
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

