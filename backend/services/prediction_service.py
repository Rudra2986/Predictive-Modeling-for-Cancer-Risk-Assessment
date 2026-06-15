from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from backend.models.prediction_log import PredictionLog

def log_prediction(
    db: Session,
    patient_data: dict,
    predicted_class: str,
    confidence_score: float,
    explanation_narrative: str,
    user_id: Optional[int] = None
) -> PredictionLog:
    """
    Saves a patient risk prediction assessment to the audit database logs.
    """
    new_log = PredictionLog(
        patient_data=patient_data,
        predicted_class=predicted_class,
        confidence_score=confidence_score,
        explanation_narrative=explanation_narrative,
        user_id=user_id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_prediction_history(db: Session, user_id: int, limit: int = 50) -> List[PredictionLog]:
    """
    Retrieves prediction query logs for a specific authenticated user account.
    """
    return db.query(PredictionLog)\
             .filter(PredictionLog.user_id == user_id)\
             .order_by(PredictionLog.created_at.desc())\
             .limit(limit)\
             .all()

def get_prediction_analytics(db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Compiles numerical aggregate data for the analytics dashboard widgets.
    """
    query = db.query(PredictionLog)
    if user_id is not None:
        query = query.filter(PredictionLog.user_id == user_id)
        
    logs = query.order_by(PredictionLog.created_at.desc()).all()
    total_assessments = len(logs)
    
    # 1. Compute risk distributions
    distribution = {"Low": 0, "Medium": 0, "High": 0}
    for log in logs:
        cls = log.predicted_class
        if cls in distribution:
            distribution[cls] += 1
            
    # 2. Extract recent runs summary list
    recent_runs = []
    for log in logs[:10]:
        recent_runs.append({
            "id": log.id,
            "cancer_type": log.patient_data.get("Cancer_Type", "Unknown"),
            "age": log.patient_data.get("Age"),
            "risk_level": log.predicted_class,
            "confidence": log.confidence_score,
            "created_at": log.created_at.isoformat()
        })
        
    # 3. Trends over time (last 7 days query volumes)
    # Generate calendar mappings
    today = datetime.now(timezone.utc).date()
    trends = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        trends[day.strftime("%Y-%m-%d")] = 0
        
    for log in logs:
        log_date_str = log.created_at.strftime("%Y-%m-%d")
        if log_date_str in trends:
            trends[log_date_str] += 1
            
    trend_list = [{"date": k, "count": v} for k, v in trends.items()]
    
    return {
        "total_assessments": total_assessments,
        "risk_distribution": distribution,
        "recent_runs": recent_runs,
        "trends": trend_list
    }
