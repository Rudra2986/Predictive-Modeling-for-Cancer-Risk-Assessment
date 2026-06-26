import os
import sys
import pytest

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.services.recommendation_service import recommendation_engine, RecommendationService

def test_lifestyle_recommendations_empty():
    """
    Verify empty context or patient data yields empty recommendations.
    """
    assert recommendation_engine.generate_lifestyle_recommendations({}) == []
    assert recommendation_engine.generate_lifestyle_recommendations({"patient_data": None}) == []

def test_lifestyle_recommendations_smoking():
    """
    Verify high smoking index triggers smoking cessation recommendation.
    """
    context = {"patient_data": {"Smoking": 7}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "Reducing tobacco intake" in recs[0]

def test_lifestyle_recommendations_obesity_and_bmi():
    """
    Verify high obesity index or high BMI triggers weight management recommendation.
    """
    context = {"patient_data": {"Obesity": 6, "BMI": 26.5}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "Maintaining a healthy weight" in recs[0]
    assert "BMI is 26.5" in recs[0]

def test_lifestyle_recommendations_alcohol():
    """
    Verify high alcohol use triggers alcohol limit recommendation.
    """
    context = {"patient_data": {"Alcohol_Use": 6}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "Limiting daily alcohol intake" in recs[0]

def test_lifestyle_recommendations_physical_activity():
    """
    Verify low physical activity levels trigger exercise recommendations.
    """
    context = {"patient_data": {"Physical_Activity": 3, "Physical_Activity_Level": 3}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "at least 150 minutes of moderate aerobic exercise" in recs[0]

def test_lifestyle_recommendations_red_meat_and_processed():
    """
    Verify high red meat or processed diet index triggers dietary improvement recommendations.
    """
    context = {"patient_data": {"Diet_Red_Meat": 7, "Diet_Salted_Processed": 8}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "limit red meat and heavily processed or salted food items" in recs[0]

def test_lifestyle_recommendations_fruit_veg():
    """
    Verify low fruit/veg intake triggers fresh portions recommendations.
    """
    context = {"patient_data": {"Fruit_Veg_Intake": 3}}
    recs = recommendation_engine.generate_lifestyle_recommendations(context)
    assert len(recs) == 1
    assert "Increasing your daily portions of fresh fruits" in recs[0]

def test_screening_guidelines_by_cancer_type():
    """
    Verify appropriate screening guidelines are attached based on cancer types.
    """
    types_to_verify = ["Breast", "Prostate", "Colon", "Lung", "Cervical"]
    for c_type in types_to_verify:
        context = {"cancer_type": c_type}
        guidelines = recommendation_engine.generate_screening_guidelines(context)
        assert len(guidelines) >= 1
        assert any(c_type in g or (c_type == "Colon" and "Colorectal" in g) or (c_type == "Cervical" and "Gynecologic" in g) for g in guidelines)

def test_screening_guidelines_genetic_and_family_history():
    """
    Verify genetic (BRCA) and family history markers trigger specific guidelines.
    """
    # BRCA Mutation
    context = {"patient_data": {"BRCA_Mutation": 1}}
    guidelines = recommendation_engine.generate_screening_guidelines(context)
    assert any("BRCA Mutation Guidance" in g for g in guidelines)

    # Family History
    context = {"patient_data": {"Family_History": 1}}
    guidelines = recommendation_engine.generate_screening_guidelines(context)
    assert any("Family History Guidance" in g for g in guidelines)

    # H. Pylori
    context = {"patient_data": {"H_Pylori_Infection": 1}}
    guidelines = recommendation_engine.generate_screening_guidelines(context)
    assert any("H. Pylori Management" in g for g in guidelines)

def test_screening_guidelines_fallback():
    """
    Verify general screening guidelines fallback is returned if no specific markers match.
    """
    guidelines = recommendation_engine.generate_screening_guidelines({})
    assert len(guidelines) == 1
    assert "General Preventive Screenings" in guidelines[0]
