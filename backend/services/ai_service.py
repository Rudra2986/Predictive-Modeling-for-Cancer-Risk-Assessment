import os
import re
from typing import List, Dict, Any, Optional

from backend.services.knowledge_service import knowledge_service
from backend.services.citation_service import citation_service
from backend.services.confidence_service import confidence_service
from backend.services.trend_analysis_service import trend_analysis_service
from backend.models.prediction_log import PredictionLog

class AIService:
    def __init__(self):
        pass

    def generate_ai_response(
        self,
        message: str,
        patient_context: dict,
        conversation_context: list,
        guardrail_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrates AI response generation.
        Checks for API keys first; falls back to the deterministic local reasoning engine if not found.
        """
        # Determine intent category dynamically from query context
        intent = self._classify_intent(message, patient_context, guardrail_category)
        
        # 1. Attempt LLM API call if keys are present
        response_text = self._generate_llm_response(message, patient_context, conversation_context)
        
        matched_topics = []
        
        # 2. Local Fallback Engine if LLM failed or is unconfigured
        if not response_text:
            response_text, matched_topics = self._fallback_local_engine(message, patient_context, conversation_context, intent)
            
        # 3. Determine confidence level using confidence service
        confidence = confidence_service.get_confidence_for_intent(intent)
        
        # 4. Generate citations
        sources = citation_service.generate_citations(intent, matched_topics)
        
        # 5. Generate follow-up suggestions
        suggestions = self._generate_suggestions(message, intent)
        
        return {
            "answer": response_text,
            "confidence": confidence,
            "sources": sources,
            "suggestions": suggestions,
            "intent": intent
        }

    def _classify_intent(self, message: str, patient_context: dict, guardrail_category: Optional[str] = None) -> str:
        """
        Helper to map user message keywords to core assistant intents.
        """
        if guardrail_category in ["PLATFORM_HELP", "ASSESSMENT_GUIDANCE"]:
            return guardrail_category

        clean_msg = message.strip().lower()
        
        # Check follow-up command overrides
        if any(x in clean_msg for x in ["simpler words", "simplify", "simple terms", "simple words"]):
            return "MEDICAL_SIMPLIFY"
        if any(x in clean_msg for x in ["anything else", "what else", "tell me more", "go on"]):
            return "MEDICAL_ANYTHING_ELSE"
            
        # Check Platform help navigation
        if any(x in clean_msg for x in ["dashboard", "assessment page", "where is", "how do i start", "prediction history"]):
            return "PLATFORM_HELP"
            
        # Check fields guidance
        if any(x in clean_msg for x in ["obesity profile", "smoking score", "family history mean", "confidence score mean", "what is shap"]):
            return "ASSESSMENT_GUIDANCE"
            
        # Check personalized comparison audits
        if any(x in clean_msg for x in ["compare", "assessments", "improved", "what changed"]):
            return "MEDICAL_TREND_COMPARISON"
            
        # Check personalized explanations
        if any(x in clean_msg for x in ["why", "prediction", "my risk", "my score", "my result"]):
            return "MEDICAL_WHY_RISK"
            
        # Check modifiable factors
        if any(x in clean_msg for x in ["improve first", "lower", "reduce"]):
            return "MEDICAL_LIFESTYLE"
            
        # Check explicit cancer keywords
        cancer_types = ["breast", "lung", "colon", "prostate", "skin", "melanoma", "cancer"]
        if any(c in clean_msg for c in cancer_types):
            return "MEDICAL_KNOWLEDGE"
            
        # Check screening keywords
        screenings = ["screening", "test", "mammogram", "colonoscopy", "ldct", "psa"]
        if any(s in clean_msg for s in screenings):
            return "MEDICAL_SCREENING"
            
        return "MEDICAL_GENERIC"

    def _generate_llm_response(
        self,
        message: str,
        patient_context: dict,
        conversation_context: list
    ) -> Optional[str]:
        """
        Calls Gemini or OpenAI SDK if credentials are present.
        """
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not gemini_key and not openai_key:
            return None
            
        system_prompt = (
            "You are OncoRisk AI Health Assistant, a professional medical assessment advisor.\n"
            "You help users interpret their cancer risk prediction scores, explain SHAP contributing factors, "
            "and provide educational lifestyle guidance.\n\n"
            "CRITICAL RULES:\n"
            "1. Never diagnose disease, prescribe medication, recommend dosages, or claim certainty. "
            "Always use educational, non-diagnostic language. Always recommend consulting a doctor.\n"
            "2. Security Boundary: Never expose source code, database credentials, internal logic, PostgreSQL "
            "schema, model weights, training details, API keys, or JWT tokens. If requested, refuse with:\n"
            "'I can only assist with health-related assessment guidance and interpretation of your OncoRisk results.'\n"
            "3. Medical Accuracy: Answer medical questions ONLY using the approved clinical knowledge base provided below. "
            "Do not make up or hallucinate medical facts.\n"
            "4. Isolation: Do not disclose data belonging to other users.\n\n"
            f"PATIENT ASSESSMENTS CONTEXT:\n{patient_context}\n\n"
            f"CONVERSATION HISTORY:\n{conversation_context}\n\n"
            "Please generate a helpful, clear, and security-safe response to the user's message."
        )
        
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=system_prompt
                )
                response = model.generate_content(message)
                return response.text.strip()
            except Exception as e:
                print(f"AI Service Warning: Gemini API Call failed: {e}. Attempting fallback...")
                
        if openai_key:
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *conversation_context,
                        {"role": "user", "content": message}
                    ]
                )
                return completion.choices[0].message.content.strip()
            except Exception as e:
                print(f"AI Service Warning: OpenAI API Call failed: {e}. Attempting fallback...")
                
        return None

    def _fallback_local_engine(
        self,
        message: str,
        patient_context: dict,
        conversation_context: list,
        intent: str
    ) -> tuple:
        """
        Local, offline-compatible reasoning engine mapping intents to context records.
        """
        response_text = ""
        matched_topics = []
        
        clean_msg = message.strip().lower()
        
        # 1. Simplification Follow-Up
        if intent == "MEDICAL_SIMPLIFY":
            last_bot_msg = None
            if conversation_context:
                for entry in reversed(conversation_context):
                    if entry.get("role") == "assistant":
                        last_bot_msg = entry.get("message")
                        break
            if last_bot_msg:
                # Strip technical jargon to simplify
                clean_text = last_bot_msg.replace("SHAP (SHapley Additive exPlanations)", "risk factor impact").strip()
                clean_text = clean_text.replace("machine learning explainer", "analysis")
                clean_text = re.sub(r"with a model confidence score of \d+%", "with high certainty", clean_text)
                response_text = f"Simply put: {clean_text}"
            else:
                response_text = "I do not have a previous response to simplify."
            return response_text, matched_topics

        # 2. Anything Else Follow-Up
        if intent == "MEDICAL_ANYTHING_ELSE":
            last_intent = None
            if conversation_context:
                for entry in reversed(conversation_context):
                    if entry.get("role") == "assistant" and entry.get("intent"):
                        last_intent = entry.get("intent")
                        break
            if last_intent == "MEDICAL_LIFESTYLE":
                response_text = (
                    "In addition to the recommendations above, focus on general wellness: "
                    "maintain standard sleep schedules (7-8 hours), hydration, and routine physical activity."
                )
            elif last_intent == "MEDICAL_SCREENING":
                response_text = (
                    "Additionally, keep a log of any unusual symptoms, complete routine physical checkups, "
                    "and review your immunizations history with a physician."
                )
            else:
                response_text = "To learn more, you can explore other dashboard elements or consult a clinician for personalized health advice."
            return response_text, matched_topics

        # 3. Platform Navigation Guidance
        if intent == "PLATFORM_HELP":
            from backend.services.platform_help_service import platform_help_service
            response_text = platform_help_service.get_help_response(message)
            return response_text, matched_topics

        # 4. Fields Guidance
        if intent == "ASSESSMENT_GUIDANCE":
            from backend.services.assessment_guidance_service import assessment_guidance_service
            response_text = assessment_guidance_service.get_guidance_response(message)
            return response_text, matched_topics

        # 5. Trend Comparison
        if intent == "MEDICAL_TREND_COMPARISON":
            # Reconstruct prediction history logs from context
            history_logs = []
            latest_dict = patient_context.get("latest_prediction")
            if latest_dict:
                # Convert back to mock PredictionLog structure
                latest_log = PredictionLog(
                    id=latest_dict.get("id"),
                    patient_data=latest_dict.get("patient_data"),
                    predicted_class=latest_dict.get("predicted_class"),
                    confidence_score=latest_dict.get("confidence_score"),
                    explanation_narrative=latest_dict.get("explanation_narrative")
                )
                history_logs.append(latest_log)
                
            for h in patient_context.get("history", []):
                h_log = PredictionLog(
                    id=h.get("id"),
                    patient_data=h.get("patient_data", {}),
                    predicted_class=h.get("predicted_class"),
                    confidence_score=h.get("confidence_score")
                )
                history_logs.append(h_log)
                
            response_text = trend_analysis_service.analyze_trends(history_logs)
            return response_text, matched_topics

        # 6. Personalized Explanations (Why is my risk High/Medium/Low)
        if intent == "MEDICAL_WHY_RISK":
            if not patient_context.get("has_history"):
                response_text = "I couldn't find a previous assessment. Complete a risk assessment first so I can provide personalized guidance."
            else:
                risk_level = patient_context.get("risk_level")
                conf_val = patient_context.get("confidence_score", 1.0) * 100
                cancer_type = patient_context.get("cancer_type", "Unknown")
                drivers = [f for f in patient_context.get("top_risk_factors", []) if f.get("shap_value", 0) > 0.005]
                
                driver_texts = []
                for drv in drivers[:3]:
                    feat = drv.get("factor")
                    val = drv.get("value")
                    driver_texts.append(f"**{feat}** (Value: {val})")
                drivers_joined = ", ".join(driver_texts)
                
                if drivers_joined:
                    response_text = (
                        f"Based on your latest assessment for suspected **{cancer_type}** cancer, "
                        f"your risk level is classified as **{risk_level}** (with a model confidence score of {conf_val:.0f}%). "
                        f"The primary risk contributors identified are {drivers_joined}. "
                        "These factors had the highest positive mathematical impact on your risk score calculation."
                    )
                else:
                    narrative = patient_context.get("explanation_narrative", "")
                    response_text = (
                        f"Your latest risk assessment category is **{risk_level}** (certainty: {conf_val:.0f}%). "
                        f"The clinical explanation generated is: \"{narrative}\""
                    )
            return response_text, matched_topics

        # 7. Modifiable Lifestyle guidance
        if intent == "MEDICAL_LIFESTYLE":
            if not patient_context.get("has_history"):
                response_text = "I couldn't find a previous assessment. Complete a risk assessment first so I can provide personalized guidance."
            else:
                from backend.services.recommendation_service import recommendation_engine
                recs = recommendation_engine.generate_lifestyle_recommendations(patient_context["latest_prediction"])
                if recs:
                    bullet_recs = "\n".join([f"* {r}" for r in recs])
                    response_text = (
                        "Based on your clinical variables and lifestyle indices from your last assessment, "
                        "here are the primary areas you should focus on to lower your overall risk factors:\n\n"
                        f"{bullet_recs}"
                    )
                else:
                    response_text = (
                        "Your latest assessment metrics reflect balanced lifestyle scores. To maintain this status, "
                        "continue focusing on standard wellness guidelines, such as avoiding tobacco and exercising regularly."
                    )
            return response_text, matched_topics

        # 8. Cancers and Screenings retrieval search
        articles = knowledge_service.search_articles(message)
        if articles:
            # Aggregate contents
            response_text = "\n\n".join([a["content"] for a in articles])
            
            # Map topics for citations service
            for a in articles:
                if "Breast" in a["title"]:
                    matched_topics.append("breast_cancer")
                elif "Lung" in a["title"]:
                    matched_topics.append("lung_cancer")
                elif "Colon" in a["title"]:
                    matched_topics.append("colon_cancer")
                elif "Prostate" in a["title"]:
                    matched_topics.append("prostate_cancer")
                elif "Skin" in a["title"]:
                    matched_topics.append("skin_cancer")
                elif "Lifestyle" in a["title"]:
                    matched_topics.append("lifestyle")
                elif "Screening" in a["title"]:
                    matched_topics.append("screening")
        else:
            is_generic_health = any(x in clean_msg for x in ["cancer", "risk", "prevention", "healthy", "guideline", "preventive"])
            if is_generic_health:
                response_text = (
                    "General Cancer Risk: Cancer risk is influenced by a combination of genetics "
                    "(such as family history or specific mutations), environmental exposures, and lifestyle "
                    "habits (such as tobacco use, diet, physical inactivity, and weight management). Keeping a healthy "
                    "BMI, eating fresh produce, exercising weekly, and consulting primary care doctors for routine checkups "
                    "are key preventive measures."
                )
                matched_topics.append("lifestyle")
            else:
                response_text = (
                    "I do not have enough information to answer that reliably. Please consult a qualified "
                    "healthcare professional."
                )
            
        return response_text, matched_topics

    def _generate_suggestions(self, message: str, intent: str) -> List[str]:
        """
        Dynamically yields contextual suggestions chips based on user intents.
        """
        clean_msg = message.lower()
        
        if "lung" in clean_msg:
            return ["What causes lung cancer?", "How can I reduce my risk?", "What screenings are available?"]
        elif "breast" in clean_msg:
            return ["What causes breast cancer?", "What is a mammogram?", "When should I get screened?"]
        elif "colon" in clean_msg or "colorectal" in clean_msg:
            return ["What causes colorectal cancer?", "What is a colonoscopy?", "What screenings are available?"]
        elif "prostate" in clean_msg:
            return ["What is a PSA test?", "What are the symptoms of prostate cancer?"]
        elif "skin" in clean_msg or "melanoma" in clean_msg:
            return ["How do I perform a skin self-exam?", "What SPF sunscreen is recommended?"]
        elif intent in ["MEDICAL_WHY_RISK", "MEDICAL_TREND_COMPARISON"]:
            return ["What should I improve first?", "Explain that in simpler words.", "Compare my assessments"]
        elif intent == "MEDICAL_LIFESTYLE":
            return ["What exercise routine is best?", "How does smoking affect risk?", "Explain that in simpler words."]
        
        return [
            "Why did I get High Risk?",
            "What should I improve first?",
            "What screenings should I consider?",
            "General cancer risk factors"
        ]

ai_service = AIService()
