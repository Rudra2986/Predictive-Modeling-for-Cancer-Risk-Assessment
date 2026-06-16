import os
import joblib
import logging
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from backend.database.session import get_db
from backend.services import prediction_service
from backend.ml.explainer import OncoRiskExplainer
from backend.api.deps import get_current_user_optional
from backend.models.user import User

router = APIRouter(prefix="/predict", tags=["prediction"])

# Set up logging
logger = logging.getLogger("backend.api.predict")

# File paths for model artifacts
MODEL_DIR = os.path.join("backend", "ml", "saved_models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.joblib")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.joblib")

# Global model references loaded at startup
best_model = None
preprocessor = None
explainer = None

# Guard to prevent infinite retraining loops per startup cycle
_retrain_attempted = False

def init_ml_models():
    global best_model, preprocessor, explainer, _retrain_attempted
    
    logger.info("Initializing ML models...")
    retrain_needed = False
    retrain_reason = ""
    
    # 1. Check if model files exist
    if not os.path.exists(MODEL_PATH) or not os.path.exists(PREPROCESSOR_PATH):
        retrain_needed = True
        retrain_reason = "Model artifacts do not exist on disk."
        logger.info(retrain_reason)
    else:
        # 2. Try to load existing model files
        try:
            best_model = joblib.load(MODEL_PATH)
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            # Pass pre-loaded instances to explainer to avoid reloading
            explainer = OncoRiskExplainer(model=best_model, preprocessor=preprocessor)
            logger.info("REST API: Loaded machine learning model and preprocessor successfully.")
        except Exception as e:
            retrain_needed = True
            retrain_reason = f"Model artifacts could not be loaded safely: {e}"
            logger.warning(f"{retrain_reason}. Triggering automatic retraining...")
            best_model = None
            preprocessor = None
            explainer = None

    # 3. Automatically retrain if needed
    if retrain_needed:
        if _retrain_attempted:
            logger.error("REST API Warning: Retraining was already attempted during this startup cycle. Aborting to prevent infinite loop.")
            return
            
        _retrain_attempted = True
        try:
            logger.info("Starting automatic model retraining (using n_trials=5 for recovery)...")
            from backend.ml.train import build_and_train
            
            # Run the training pipeline synchronously with reduced trials to speed up Render startup
            build_and_train(n_trials=5)
            
            logger.info("Automatic model retraining completed. Reloading fresh artifacts...")
            
            # Reload fresh artifacts
            best_model = joblib.load(MODEL_PATH)
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            explainer = OncoRiskExplainer(model=best_model, preprocessor=preprocessor)
            
            logger.info(f"REST API: Fresh model and preprocessor loaded successfully from paths: {MODEL_PATH}, {PREPROCESSOR_PATH}")
        except Exception as retrain_error:
            logger.error(f"REST API Critical Error: Automatic model retraining failed: {retrain_error}", exc_info=True)
            # Ensure the backend never crashes: keep them as None and let uvicorn startup continue
            best_model = None
            preprocessor = None
            explainer = None

# Trigger loading on module import
init_ml_models()

# Class index to label mapping
IDX_TO_LABEL = {0: "Low", 1: "Medium", 2: "High"}

# Input request schema
class PatientPredictionInput(BaseModel):
    Age: int = Field(..., ge=0, le=120, description="Age of the patient")
    Gender: int = Field(..., ge=0, le=1, description="Gender (0 = Female, 1 = Male)")
    Smoking: int = Field(..., ge=0, le=10, description="Smoking habits index (0-10)")
    Alcohol_Use: int = Field(..., ge=0, le=10, description="Alcohol use index (0-10)")
    Obesity: int = Field(..., ge=0, le=10, description="Obesity level index (0-10)")
    Family_History: int = Field(..., ge=0, le=1, description="Family history of cancer (0 = No, 1 = Yes)")
    Diet_Red_Meat: int = Field(..., ge=0, le=10, description="Diet frequency of red meat index (0-10)")
    Diet_Salted_Processed: int = Field(..., ge=0, le=10, description="Diet frequency of processed food index (0-10)")
    Fruit_Veg_Intake: int = Field(..., ge=0, le=10, description="Diet frequency of fruits/vegetables index (0-10)")
    Physical_Activity: int = Field(..., ge=0, le=10, description="Physical activity frequency index (0-10)")
    Air_Pollution: int = Field(..., ge=0, le=10, description="Air pollution exposure index (0-10)")
    Occupational_Hazards: int = Field(..., ge=0, le=10, description="Occupational hazard exposure index (0-10)")
    BRCA_Mutation: int = Field(..., ge=0, le=1, description="BRCA mutation present (0 = No, 1 = Yes)")
    H_Pylori_Infection: int = Field(..., ge=0, le=1, description="H. Pylori infection present (0 = No, 1 = Yes)")
    Calcium_Intake: int = Field(..., ge=0, le=10, description="Calcium intake index (0-10)")
    BMI: float = Field(..., ge=10.0, le=60.0, description="Body Mass Index (BMI)")
    Physical_Activity_Level: int = Field(..., ge=0, le=10, description="Active exercise level index (0-10)")
    Cancer_Type: Optional[str] = Field("Unknown", description="Type of cancer under analysis (e.g. Breast, Colon, Lung)")

# Output response schemas
class ContributingFactorSchema(BaseModel):
    factor: str
    category: str
    value: float
    impact_level: str
    impact: str  # For spec compatibility (Low, Medium, High)
    shap_value: float  # Dynamic SHAP value contribution

class PredictionResponseSchema(BaseModel):
    prediction: str
    confidence_score: float
    explanation_narrative: str
    contributing_factors: List[ContributingFactorSchema]

@router.post("", response_model=PredictionResponseSchema)
def predict_cancer_risk(
    patient_in: PatientPredictionInput,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Perform a machine learning assessment of cancer risk for a patient profile.
    Saves prediction metadata to database. Supports authenticated and guest users.
    """
    if not best_model or not preprocessor or not explainer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML model is unavailable. Retraining may still be in progress."
        )
    
    # Extract features dict
    patient_data = patient_in.model_dump()
    
    try:
        # Preprocessor expects a Pandas DataFrame structure
        patient_df = pd.DataFrame([patient_data])
        X_processed = preprocessor.transform(patient_df)
        
        # Predict target class
        pred_idx = best_model.predict(X_processed)[0]
        predicted_class = IDX_TO_LABEL[int(pred_idx)]
        
        # Get prediction confidence score
        if hasattr(best_model, "predict_proba"):
            probs = best_model.predict_proba(X_processed)[0]
            confidence_score = float(probs[pred_idx])
        else:
            confidence_score = 1.0
            
        # Generate model explanation and clinical narrative
        explanation = explainer.explain_prediction(
            patient_data=patient_data,
            prediction=predicted_class,
            confidence_score=confidence_score
        )
        
        # Map output factors list
        raw_factors = explanation.get("contributing_factors", [])
        contributing_factors = []
        for factor in raw_factors:
            contributing_factors.append({
                "factor": factor["factor"],
                "category": factor["category"],
                "value": float(factor["value"]),
                "impact_level": factor["impact_level"],
                "impact": factor["impact_level"],
                "shap_value": float(factor.get("shap_value", 0.0))
            })
            
        explanation_narrative = explanation.get("explanation_narrative", "")
        
        # Save to database logs
        user_id = current_user.id if current_user else None
        prediction_service.log_prediction(
            db=db,
            patient_data=patient_data,
            predicted_class=predicted_class,
            confidence_score=confidence_score,
            explanation_narrative=explanation_narrative,
            user_id=user_id
        )
        
        return {
            "prediction": predicted_class,
            "confidence_score": confidence_score,
            "explanation_narrative": explanation_narrative,
            "contributing_factors": contributing_factors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Inference execution failed: {str(e)}"
        )
