from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from backend.api.deps import get_current_user
from backend.models.user import User
from backend.services.retrain_service import retrain_service
from backend.ml.train import build_and_train
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/admin", tags=["admin & retraining"])

class RetrainStatusResponseSchema(BaseModel):
    is_training: bool
    current_step: str
    current_trial: int
    total_trials: int
    best_rf_f1: float
    best_xgb_f1: float
    best_f1: float
    winner_model: str
    logs: List[str]
    error: Optional[str]
    completed_at: Optional[str]

class RetrainRequestSchema(BaseModel):
    trials_per_model: int = 15

@router.post("/retrain", status_code=status.HTTP_202_ACCEPTED)
def trigger_retraining(
    background_tasks: BackgroundTasks,
    payload: Optional[RetrainRequestSchema] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger Optuna hyperparameter optimization and model retraining in the background.
    """
    if retrain_service.is_training:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A model retraining process is already in progress."
        )
        
    n_trials = payload.trials_per_model if payload else 15
    # Start background execution
    background_tasks.add_task(build_and_train, n_trials=n_trials)
    return {"message": "Model retraining successfully initiated in background thread."}

@router.get("/retrain/status", response_model=RetrainStatusResponseSchema)
def get_retraining_status(current_user: User = Depends(get_current_user)):
    """
    Get live progress status, trials completed, and log streams for the retraining run.
    """
    return {
        "is_training": retrain_service.is_training,
        "current_step": retrain_service.current_step,
        "current_trial": retrain_service.current_trial,
        "total_trials": retrain_service.total_trials,
        "best_rf_f1": retrain_service.best_rf_f1,
        "best_xgb_f1": retrain_service.best_xgb_f1,
        "best_f1": retrain_service.best_f1,
        "winner_model": retrain_service.winner_model,
        "logs": retrain_service.logs,
        "error": retrain_service.error,
        "completed_at": retrain_service.completed_at
    }
