from typing import List, Optional

class CitationService:
    def generate_citations(self, intent: str, matched_topics: Optional[List[str]] = None) -> List[str]:
        """
        Attaches human-readable source citations to the chatbot response.
        Never exposes database schemas, files, or internal code modules.
        """
        citations = []
        
        # 1. Attach Knowledge Base citations
        if matched_topics:
            for topic in matched_topics:
                topic_title = topic.replace("_", " ").title()
                citations.append(f"Knowledge Base: {topic_title}")

        # 2. Attach intent-specific dynamic sources
        if not intent:
            return citations
            
        intent_upper = intent.upper()
        if intent_upper in ["MEDICAL_WHY_RISK", "MEDICAL_PERSONALIZED", "MEDICAL_SHAP_ANALYSIS"]:
            citations.append("Latest Prediction Analysis")
            citations.append("SHAP Feature Importance Explainer")
        elif intent_upper == "MEDICAL_TREND_COMPARISON":
            citations.append("Trend Analysis Engine")
        elif intent_upper in ["MEDICAL_LIFESTYLE", "MEDICAL_SCREENING"]:
            citations.append("OncoRisk Recommendation Rules")
        elif intent_upper in ["PLATFORM_HELP", "ASSESSMENT_GUIDANCE"]:
            citations.append("Platform Help Content")

        # Fallback if no specific category was found but query was clinical
        if not citations and intent_upper.startswith("MEDICAL_"):
            citations.append("General Cancer Risk Framework")

        # Return unique list
        return list(dict.fromkeys(citations))

citation_service = CitationService()
