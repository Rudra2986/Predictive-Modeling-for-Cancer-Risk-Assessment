import re
import logging
from typing import Tuple, Optional

# Set up dedicated security logger
logger = logging.getLogger("backend.security.chatbot")

class GuardrailService:
    # Intent category constants
    SECURITY_SENSITIVE = "SECURITY_SENSITIVE"
    PLATFORM_HELP = "PLATFORM_HELP"
    ASSESSMENT_GUIDANCE = "ASSESSMENT_GUIDANCE"
    MEDICAL_QUERY = "MEDICAL_QUERY"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"

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
            r"admin\s*password",
            
            # Additional Administrative & Infrastructure blocks
            r"other\s+user",
            r"another\s+user",
            r"database\s+schema",
            r"database\s+tables?",
            r"postgresql\s+tables?",
            r"postgresql\s+schema",
            r"backend\s+code",
            r"project\s+structure",
            r"implementation\s+details",
            r"render\s+credential",
            r"deployment\s+config",
            r"admin\s+account",
            r"list\s+all\s+users",
            r"export\s+user\s+data",
            
            # Model Internals blocks
            r"model\s*weights",
            r"shap\s*thresholds?",
            r"training\s*data",
            r"scoring\s*formulas?",
            r"feature\s*engineering",
            r"risk\s*calculation",
            r"how\s+much\s+does\s+.*\s+affect\s+the\s+model",
            r"how\s+is\s+the\s+model\s+trained"
        ]
        
        # Synonym lists for PLATFORM_HELP questions
        self.history_aliases = [
            "history", "my history", "view history", "show history",
            "prediction history", "assessment history", "previous assessments"
        ]
        self.assessment_aliases = [
            "run assessment", "start assessment", "new assessment",
            "take assessment", "perform assessment", "begin assessment",
            "assessment page", "where is the assessment page", "where is the run assessment page"
        ]
        self.dashboard_aliases = [
            "dashboard", "access dashboard", "view dashboard"
        ]
        self.workflow_aliases = [
            "after prediction", "after getting a prediction", "after receiving a prediction", 
            "next steps", "compare assessments", "compare previous predictions", 
            "improve risk factors", "reduce risk factors", "improve my risk"
        ]

        # Regexes for ASSESSMENT_GUIDANCE questions
        self.assessment_guidance_patterns = [
            r"smoking\s+(score|habits|index)",
            r"what\s+should\s+i\s+enter\s+for\s+smoking",
            r"smoking\s+intensity",
            r"smoking\s+frequency",
            r"alcohol\s+(consumption|use|habits|index)",
            r"what\s+does\s+alcohol\s+consumption\s+mean",
            r"family\s+history",
            r"what\s+should\s+i\s+enter\s+for\s+family\s+history",
            r"what\s+does\s+family\s+history\s+mean",
            r"physical\s+activity",
            r"what\s+is\s+physical\s+activity\s+level",
            r"air\s+pollution",
            r"what\s+does\s+air\s+pollution\s+exposure\s+mean",
            r"obesity\s+profile\s+index",
            r"obesity\s+index",
            r"what\s+is\s+obesity\s+profile\s+index",
            r"what\s+does\s+obesity\s+profile\s+mean",
            r"confidence\s+score",
            r"explain\s+confidence\s+score",
            r"what\s+does\s+confidence\s+score\s+mean",
            r"shap\s+explainability",
            r"what\s+is\s+shap",
            r"shap\s+values?",
            r"shapley",
            r"what\s+does\s+this\s+field\s+mean",
            r"field\s+descriptions?",
            r"explain\s+fields?"
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

    def classify_message(self, message: str, user_id: int) -> Tuple[str, Optional[str]]:
        """
        Classifies the incoming user message into an intent category.
        Returns a tuple of (category, reason_if_blocked).
        
        Processing order:
        1. Security Check
        2. Platform Help Check
        3. Assessment Guidance Check
        4. Medical Query Check
        5. Out of Scope fallback
        """
        # Normalize whitespace and case
        clean_msg = " ".join(message.strip().lower().split())

        # 1. Security Check
        for pattern in self.forbidden_patterns:
            if re.search(pattern, clean_msg):
                reason = "Potential credential request" if "credential" in pattern or "password" in pattern else \
                         "Potential system information request" if "code" in pattern or "file" in pattern or "env" in pattern else \
                         "Security-sensitive request"
                self._log_rejection(user_id, message, reason)
                return self.SECURITY_SENSITIVE, reason

        # 2. Platform Help Check
        is_platform_help = (
            any(alias in clean_msg for alias in self.history_aliases) or
            any(alias in clean_msg for alias in self.assessment_aliases) or
            any(alias in clean_msg for alias in self.dashboard_aliases) or
            any(alias in clean_msg for alias in self.workflow_aliases)
        )
        if is_platform_help:
            return self.PLATFORM_HELP, None

        # 3. Assessment Guidance Check
        for pattern in self.assessment_guidance_patterns:
            if re.search(pattern, clean_msg):
                return self.ASSESSMENT_GUIDANCE, None

        # 4. Medical Query Check
        # Match explicit intents first
        for intent in self.allowed_intents:
            if re.search(intent, clean_msg):
                return self.MEDICAL_QUERY, None
        
        # Match keywords next
        words = re.findall(r"\b\w+\b", clean_msg)
        matched_keywords = [w for w in words if w in self.allowed_vocab]
        if matched_keywords:
            return self.MEDICAL_QUERY, None

        # 5. Out of Scope fallback
        reason = "Out-of-scope request"
        self._log_rejection(user_id, message, reason)
        return self.OUT_OF_SCOPE, reason

    def validate_message(self, message: str, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Maintains backwards compatibility.
        Returns:
            (is_allowed: bool, rejection_reason: Optional[str])
        """
        category, reason = self.classify_message(message, user_id)
        if category in [self.SECURITY_SENSITIVE, self.OUT_OF_SCOPE]:
            return False, reason
        return True, None

    def _log_rejection(self, user_id: int, message: str, reason: str) -> None:
        """
        Logs a security warning when a request is blocked.
        """
        logger.warning(
            f"Chatbot Rejection: User ID: {user_id} | Reason: {reason} | Original Message: '{message}'"
        )

# Instantiate global service instance
guardrail = GuardrailService()

