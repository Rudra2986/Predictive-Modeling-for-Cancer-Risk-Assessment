import hashlib
import time
from collections import OrderedDict
from typing import Optional, Dict, Any

class CacheService:
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 86400):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        # In-memory LRU cache dictionary: key -> {"value": dict, "timestamp": float}
        self._cache: OrderedDict = OrderedDict()
        
        # Define intents allowed to be cached (purely general, educational/platform help)
        self.cacheable_intents = {
            "MEDICAL_KNOWLEDGE",
            "MEDICAL_SCREENING",
            "MEDICAL_GENERIC",
            "PLATFORM_HELP",
            "ASSESSMENT_GUIDANCE"
        }

    def is_personalized(self, question: str, intent: str) -> bool:
        """
        Determines if a query is user-specific or personalized.
        Personalized queries must never be cached.
        """
        clean = " ".join(question.strip().lower().split())
        
        # Disallowed exact queries or close variants
        disallowed_exact = {
            "why is my risk high",
            "compare my assessments",
            "explain my prediction",
            "explain my result",
            "has my risk improved",
            "what changed most",
            "why did i get high risk",
            "why did i get medium risk",
            "why did i get low risk",
            "why is my risk medium",
            "why is my risk low",
            "what is my risk",
            "what is my score",
            "what was my result",
            "show my prediction",
            "what should i improve first",
            "what factors affected my prediction",
            "explain my assessment"
        }
        if clean in disallowed_exact:
            return True
            
        # Check for personal pronouns indicating user-specific context
        import re
        words = set(re.findall(r"\b\w+\b", clean))
        personal_pronouns = {"my", "me", "i", "mine", "myself"}
        if words.intersection(personal_pronouns):
            return True
            
        # Check for intent categories that are personalized
        personalized_intents = {
            "MEDICAL_WHY_RISK",
            "MEDICAL_TREND_COMPARISON",
            "MEDICAL_LIFESTYLE",
            "MEDICAL_SIMPLIFY",
            "MEDICAL_ANYTHING_ELSE",
            "MEDICAL_NO_HISTORY"
        }
        if intent and intent.upper() in personalized_intents:
            return True
            
        return False

    def _generate_key(self, question: str, context_hash: str) -> str:
        """
        Generates a secure SHA256 key from the question and context hash.
        """
        raw = f"{question.strip().lower()}:{context_hash}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, question: str, context_hash: str, intent: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves cached response if valid (matches key, intent cacheable, not personalized, and TTL not expired).
        """
        if not intent or intent.upper() not in self.cacheable_intents:
            return None

        if self.is_personalized(question, intent):
            return None

        key = self._generate_key(question, context_hash)
        
        if key in self._cache:
            entry = self._cache[key]
            now = time.time()
            if now - entry["timestamp"] < self.ttl_seconds:
                # Move to end (LRU hit)
                self._cache.move_to_end(key)
                return entry["value"]
            else:
                # Expired key
                del self._cache[key]
        return None

    def set(self, question: str, context_hash: str, intent: str, value: Dict[str, Any]) -> None:
        """
        Saves a response to the cache if the intent category is allowed and query is not personalized.
        """
        if not intent or intent.upper() not in self.cacheable_intents:
            return

        if self.is_personalized(question, intent):
            return

        key = self._generate_key(question, context_hash)
        now = time.time()
        
        # Evict oldest if limit reached and key is new
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False) # pop oldest key (first item)

        self._cache[key] = {
            "value": value,
            "timestamp": now
        }

    def clear(self) -> None:
        """
        Clears the cache content.
        """
        self._cache.clear()

cache_service = CacheService()
