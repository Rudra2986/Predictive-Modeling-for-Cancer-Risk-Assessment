import re
import logging
from typing import Tuple, Optional

# Set up dedicated security logger
logger = logging.getLogger("backend.security.chatbot")

class GuardrailService:
    def __init__(self):
        # Forbidden regexes targeting credentials, source code, environment, hacking attempts, etc.
        self.forbidden_patterns = [
            r"source\s*code",
            r"project\s*files?",
            r"directory\s*structure",
            r"database\s*password",
            r"database\s*credential",
            r"postgres\s*password",
            r"postgres\s*credential",
            r"render\s*db",
            r"render\s*database",
            r"sql\s*injection",
            r"select\s+\*\s+from",
            r"drop\s+table",
            r"delete\s+from",
            r"show\s+all\s+users",
            r"env(ironment)?\s*variables?",
            r"jwt\s*secret",
            r"jwt\s*token",
            r"auth\s*token",
            r"api\s*keys?",
            r"config\.json",
            r"github\s*repo",
            r"github\s*repository",
            r"docker-compose",
            r"render\.yaml",
            r"admin\s*credential",
            r"admin\s*password"
        ]
        
        # Allow-list health/clinical vocabulary words
        self.allowed_vocab = {
            "risk", "factor", "lifestyle", "diet", "improve", "exercise", "smoke", 
            "smoking", "alcohol", "obesity", "prevent", "health", "screen", 
            "screening", "mammogram", "colonoscopy", "prediction", "why", 
            "result", "shap", "explanation", "history", "low", "medium", "high", 
            "assess", "assessment", "audit", "log", "cancer", "lung", "prostate", 
            "breast", "colon", "rectal", "stomach", "liver", "kidney", "bladder", 
            "pancreas", "pancreatic", "skin", "ovarian", "cervical", "testicular", 
            "thyroid", "leukemia", "lymphoma", "obese", "overweight", "bmi", 
            "activity", "physical", "fit", "fitness", "brca", "gene", "genetic", 
            "mutation", "hereditary", "family", "age", "gender", "vitals", 
            "calcium", "fruit", "vegetable", "processed", "meat", "salted", 
            "pollution", "occupational", "hazard", "workplace", "asbestos", 
            "radiation", "chemical", "pylori", "infection", "gastric", "advice",
            "clinical", "patient", "score", "metric", "level", "diagnose", "doctor"
        }
        
        # Intent expressions that represent valid medical questions
        self.allowed_intents = [
            r"why\s+is\s+my\s+score\s+high",
            r"why\s+did\s+i\s+get\s+this\s+result",
            r"what\s+should\s+i\s+improve",
            r"what\s+should\s+i\s+focus\s+on\s+first",
            r"explain\s+my\s+assessment",
            r"what\s+factors\s+affected\s+my\s+prediction",
            r"how\s+can\s+i\s+reduce\s+my\s+risk",
            r"what\s+did\s+my\s+results?\s+mean",
            r"explain\s+my\s+results?",
            r"what\s+should\s+i\s+focus\s+on",
            r"how\s+to\s+lower\s+my\s+risk",
            r"why\s+did\s+i\s+get\s+medium\s+risk",
            r"why\s+did\s+i\s+get\s+high\s+risk",
            r"why\s+did\s+i\s+get\s+low\s+risk",
            r"why\s+is\s+my\s+risk\s+medium",
            r"why\s+is\s+my\s+risk\s+high",
            r"why\s+is\s+my\s+risk\s+low"
        ]

    def validate_message(self, message: str, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validates if the user query is safe and inside the approved topics allow-list.
        Returns:
            (is_allowed: bool, rejection_reason: Optional[str])
        """
        clean_msg = message.strip().lower()
        
        # 1. Hacking & Security Guardrails check
        for pattern in self.forbidden_patterns:
            if re.search(pattern, clean_msg):
                reason = "Potential credential request" if "credential" in pattern or "password" in pattern else \
                         "Potential system information request" if "code" in pattern or "file" in pattern or "env" in pattern else \
                         "Security-sensitive request"
                self._log_rejection(user_id, message, reason)
                return False, reason
                
        # 2. Intent-Based matching
        for intent in self.allowed_intents:
            if re.search(intent, clean_msg):
                return True, None
                
        # 3. Allow-list Keyword check
        words = re.findall(r"\b\w+\b", clean_msg)
        matched_keywords = [w for w in words if w in self.allowed_vocab]
        
        if matched_keywords:
            return True, None
            
        # If no allowed intent or keyword matches, reject as out-of-scope
        reason = "Out-of-scope request"
        self._log_rejection(user_id, message, reason)
        return False, reason

    def _log_rejection(self, user_id: int, message: str, reason: str) -> None:
        """
        Logs a security warning when a request is blocked.
        """
        logger.warning(
            f"Chatbot Rejection: User ID: {user_id} | Reason: {reason} | Original Message: '{message}'"
        )

# Instantiate global service instance
guardrail = GuardrailService()
