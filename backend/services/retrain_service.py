import time
from typing import List, Dict, Any, Optional

class RetrainService:
    """
    Singleton service to track, log, and monitor background ML engine retraining runs.
    Tracks active trial progress and study parameters during Optuna search.
    """
    def __init__(self):
        self.is_training: bool = False
        self.current_step: str = "Idle"
        self.current_trial: int = 0
        self.total_trials: int = 30  # Will be dynamically set
        self.n_trials: int = 15     # Will be dynamically set
        self.best_rf_f1: float = 0.0
        self.best_xgb_f1: float = 0.0
        self.best_f1: float = 0.0
        self.winner_model: str = "None"
        self.logs: List[str] = []
        self.error: Optional[str] = None
        self.completed_at: Optional[str] = None

    def reset(self, n_trials: int = 15):
        self.is_training = True
        self.current_step = "Starting retraining..."
        self.current_trial = 0
        self.n_trials = n_trials
        self.total_trials = n_trials * 2  # n_trials RF + n_trials XGBoost
        self.best_rf_f1 = 0.0
        self.best_xgb_f1 = 0.0
        self.best_f1 = 0.0
        self.winner_model = "None"
        self.logs = []
        self.error = None
        self.completed_at = None

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        self.logs.append(log_msg)
        print(log_msg)

    def complete(self, winner_model: str, best_f1: float):
        self.is_training = False
        self.current_step = "Completed"
        self.winner_model = winner_model
        self.best_f1 = best_f1
        self.completed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"Retraining completed successfully! Winner: {winner_model} (Weighted F1: {best_f1:.4f})")

    def fail(self, error_msg: str):
        self.is_training = False
        self.current_step = "Failed"
        self.error = error_msg
        self.completed_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"ERROR: Retraining failed: {error_msg}")

    def update_trial(self, trial_num: int, model_type: str, f1: float):
        self.current_trial = trial_num
        if model_type == "Random Forest":
            if f1 > self.best_rf_f1:
                self.best_rf_f1 = f1
            best_current = self.best_rf_f1
            display_trial = trial_num + 1
        else:
            if f1 > self.best_xgb_f1:
                self.best_xgb_f1 = f1
            best_current = self.best_xgb_f1
            display_trial = (trial_num - self.n_trials) + 1
            
        self.log(f"[{model_type}] Trial {display_trial}/{self.n_trials} completed. Trial F1: {f1:.4f}. Best {model_type} F1: {best_current:.4f}")

# Instantiate singleton instance
retrain_service = RetrainService()
