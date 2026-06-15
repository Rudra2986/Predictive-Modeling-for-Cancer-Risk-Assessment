from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.database.session import get_db
from backend.services import prediction_service
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/predictions", tags=["history & analytics"])

# Pydantic validation schemas
class PredictionHistoryItem(BaseModel):
    id: int
    patient_data: Dict[str, Any]
    predicted_class: str
    confidence_score: float
    explanation_narrative: str
    created_at: datetime

    class Config:
        from_attributes = True

class RecentRunSchema(BaseModel):
    id: int
    cancer_type: str
    age: Optional[int]
    risk_level: str
    confidence: float
    created_at: str

class TrendItemSchema(BaseModel):
    date: str
    count: int

class AnalyticsResponseSchema(BaseModel):
    total_assessments: int
    risk_distribution: Dict[str, int]
    recent_runs: List[RecentRunSchema]
    trends: List[TrendItemSchema]

@router.get("/history", response_model=List[PredictionHistoryItem])
def get_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve prediction query history logs for the current authenticated user.
    """
    history = prediction_service.get_prediction_history(db=db, user_id=current_user.id, limit=limit)
    return history

@router.get("/analytics", response_model=AnalyticsResponseSchema)
def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch numerical aggregate data and query trends for the user's dashboard widgets.
    """
    analytics = prediction_service.get_prediction_analytics(db=db, user_id=current_user.id)
    return analytics
