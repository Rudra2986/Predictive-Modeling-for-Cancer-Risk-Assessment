class ConfidenceService:
    # Intent category constants mapped to confidence levels
    HIGH_INTENTS = {
        "MEDICAL_WHY_RISK",
        "MEDICAL_TREND_COMPARISON",
        "MEDICAL_SHAP_ANALYSIS",
        "MEDICAL_PERSONALIZED"
    }
    
    MEDIUM_INTENTS = {
        "MEDICAL_KNOWLEDGE",
        "MEDICAL_SCREENING",
        "MEDICAL_GENERIC",
        "PLATFORM_HELP",
        "ASSESSMENT_GUIDANCE",
        "MEDICAL_LIFESTYLE"
    }

    def get_confidence_for_intent(self, intent: str) -> str:
        """
        Determines the confidence score independently of the AI provider based on classification rules.
        """
        if not intent:
            return "LOW"
            
        intent_upper = intent.upper()
        if intent_upper in self.HIGH_INTENTS:
            return "HIGH"
        elif intent_upper in self.MEDIUM_INTENTS:
            return "MEDIUM"
        else:
            return "LOW"

confidence_service = ConfidenceService()
