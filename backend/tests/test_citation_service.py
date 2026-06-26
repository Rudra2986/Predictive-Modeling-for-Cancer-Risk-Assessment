import os
import sys
import pytest

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.services.citation_service import citation_service

def test_citation_knowledge_base():
    """
    Verify matched topics are correctly formatted as knowledge base citations.
    """
    topics = ["lung_cancer", "diet_and_exercise", "genetics"]
    citations = citation_service.generate_citations(intent="", matched_topics=topics)
    
    assert len(citations) == 3
    assert "Knowledge Base: Lung Cancer" in citations
    assert "Knowledge Base: Diet And Exercise" in citations
    assert "Knowledge Base: Genetics" in citations

def test_citation_intent_specific():
    """
    Verify intent-specific sources are correctly attached.
    """
    # Prediction/SHAP intents
    cit_shap = citation_service.generate_citations(intent="MEDICAL_SHAP_ANALYSIS")
    assert "Latest Prediction Analysis" in cit_shap
    assert "SHAP Feature Importance Explainer" in cit_shap

    # Trend comparisons
    cit_trend = citation_service.generate_citations(intent="MEDICAL_TREND_COMPARISON")
    assert "Trend Analysis Engine" in cit_trend

    # Lifestyle/Screening
    cit_lifestyle = citation_service.generate_citations(intent="MEDICAL_LIFESTYLE")
    assert "OncoRisk Recommendation Rules" in cit_lifestyle

    # Platform/Assessment guidance
    cit_help = citation_service.generate_citations(intent="PLATFORM_HELP")
    assert "Platform Help Content" in cit_help

def test_citation_fallback_medical():
    """
    Verify any other MEDICAL_ intent falls back to 'General Cancer Risk Framework'.
    """
    citations = citation_service.generate_citations(intent="MEDICAL_UNKNOWN_FUTURE_INTENT")
    assert citations == ["General Cancer Risk Framework"]

def test_citation_empty_or_non_medical():
    """
    Verify non-medical/empty intents return no citations unless topics matched.
    """
    assert citation_service.generate_citations(intent="") == []
    assert citation_service.generate_citations(intent="OUT_OF_SCOPE") == []

def test_citation_uniqueness():
    """
    Verify citations list does not contain duplicate values.
    """
    # Even if we pass duplicates or overlap, results should be unique
    topics = ["lung_cancer", "lung_cancer"]
    citations = citation_service.generate_citations(intent="MEDICAL_TREND_COMPARISON", matched_topics=topics)
    
    # We should have exactly two unique items
    assert len(citations) == 2
    assert citations.count("Knowledge Base: Lung Cancer") == 1
    assert citations.count("Trend Analysis Engine") == 1
