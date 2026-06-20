import re

class PromptSecurityService:
    def __init__(self):
        # Case-insensitive patterns checking for prompt injections, system prompt disclosures, or rule override attempts
        self.injection_patterns = [
            r"ignore\s+.*(instruction|prompt|rule|guideline|command|check|safety)",
            r"override\s+.*(system|safety|prior|security|restriction)",
            r"act\s+as\s+.*(admin|administrator|root|developer)",
            r"you\s+are\s+now\s+.*(admin|administrator|root|developer)",
            r"reveal\s+.*(hidden|system|internal|prompt|instruction|rule)",
            r"show\s+.*(hidden|system|internal|prompt|instruction|rule|guideline)",
            r"what\s+is\s+your\s+system\s+prompt",
            r"what\s+are\s+your\s+system\s+instructions",
            r"reveal\s+prompt",
            r"print\s+.*(instruction|system|message)",
            r"bypass\s+.*(safety|restriction|rule|guardrail|system)",
            r"jailbreak",
            r"forget\s+.*(instruction|prompt|rule|command|rules)",
            r"do\s+not\s+follow\s+.*(instruction|prompt|rule)",
            r"developer\s+mode"
        ]

    def is_prompt_injection(self, message: str) -> bool:
        """
        Validates if the incoming message contains prompt injection, override, 
        or bypass patterns. Returns True if injection is detected.
        """
        clean_msg = " ".join(message.strip().lower().split())
        for pattern in self.injection_patterns:
            if re.search(pattern, clean_msg):
                return True
        return False

prompt_security_service = PromptSecurityService()
