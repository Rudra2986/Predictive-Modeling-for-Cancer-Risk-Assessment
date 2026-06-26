import os
import sys
import pytest

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.services.confidence_service import confidence_service

def test_confidence_high_intents():
    """
    Verify intents mapped to HIGH confidence level return 'HIGH'.
    """
    high_intents = ["MEDICAL_WHY_RISK", "MEDICAL_TREND_COMPARISON", "MEDICAL_SHAP_ANALYSIS", "MEDICAL_PERSONALIZED"]
    for intent in high_intents:
        assert confidence_service.get_confidence_for_intent(intent) == "HIGH"
        # Test case insensitivity
        assert confidence_service.get_confidence_for_intent(intent.lower()) == "HIGH"

def test_confidence_medium_intents():
    """
    Verify intents mapped to MEDIUM confidence level return 'MEDIUM'.
    """
    medium_intents = [
        "MEDICAL_KNOWLEDGE",
        "MEDICAL_SCREENING",
        "MEDICAL_GENERIC",
        "PLATFORM_HELP",
        "ASSESSMENT_GUIDANCE",
        "MEDICAL_LIFESTYLE",
        "MEDICAL_SIMPLIFY",
        "MEDICAL_ANYTHING_ELSE"
    ]
    for intent in medium_intents:
        assert confidence_service.get_confidence_for_intent(intent) == "MEDIUM"
        # Test case insensitivity
        assert confidence_service.get_confidence_for_intent(intent.lower()) == "MEDIUM"

def test_confidence_low_or_invalid_intents():
    """
    Verify undefined or empty intents return 'LOW'.
    """
    assert confidence_service.get_confidence_for_intent("OUT_OF_SCOPE") == "LOW"
    assert confidence_service.get_confidence_for_intent("SOMETHING_ELSE") == "LOW"
    assert confidence_service.get_confidence_for_intent("") == "LOW"
    assert confidence_service.get_confidence_for_intent(None) == "LOW"
