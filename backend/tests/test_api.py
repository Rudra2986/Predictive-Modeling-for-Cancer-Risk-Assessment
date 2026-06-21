import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app
from backend.database.session import get_db, SessionLocal
from backend.models.user import User
from backend.models.prediction_log import PredictionLog

client = TestClient(app)

def test_health_check():
    """
    Verify health endpoint works.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data
    assert "ml_model" in data
    assert "explainer" in data
    assert data["version"] == "1.0.0"

def test_api_workflow():
    """
    Verify full user registration, authentication, ML prediction,
    and history/analytics endpoints flow.
    """
    import time
    import backend.api.predict as predict
    for _ in range(600):
        with predict.model_loading_lock:
            if predict.model_ready:
                break
        time.sleep(0.1)
        
    db = SessionLocal()
    
    # 1. Clean up any previous test user
    test_email = "api_integration_test@oncorisk.ai"
    existing = db.query(User).filter(User.email == test_email).first()
    if existing:
        db.delete(existing)
        db.commit()
        
    try:
        # 2a. Test user registration with simple/invalid password
        invalid_register_payload = {
            "email": test_email,
            "password": "short"
        }
        resp = client.post("/api/auth/register", json=invalid_register_payload)
        assert resp.status_code == 422
        
        # 2b. Test user registration with password missing uppercase
        invalid_register_payload_2 = {
            "email": test_email,
            "password": "validlengthbutnouror123!"
        }
        resp = client.post("/api/auth/register", json=invalid_register_payload_2)
        assert resp.status_code == 422
        
        # 2c. Test user registration with compliant password
        register_payload = {
            "email": test_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/register", json=register_payload)
        assert resp.status_code == 201
        user_data = resp.json()
        assert user_data["email"] == test_email
        assert "id" in user_data
        assert user_data["is_admin"] is False
        
        # 3. Test user login
        login_payload = {
            "email": test_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/login", json=login_payload)
        assert resp.status_code == 200
        token_data = resp.json()
        assert "access_token" in token_data
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 4. Test current user /me endpoint
        resp = client.get("/api/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == test_email
        assert resp.json()["is_admin"] is False
        
        # 5. Test model prediction as guest
        prediction_payload = {
            "Age": 55,
            "Gender": 1,
            "Smoking": 7,
            "Alcohol_Use": 9,
            "Obesity": 8,
            "Family_History": 0,
            "Diet_Red_Meat": 4,
            "Diet_Salted_Processed": 6,
            "Fruit_Veg_Intake": 3,
            "Physical_Activity": 2,
            "Air_Pollution": 2,
            "Occupational_Hazards": 10,
            "BRCA_Mutation": 0,
            "H_Pylori_Infection": 0,
            "Calcium_Intake": 4,
            "BMI": 27.0,
            "Physical_Activity_Level": 6,
            "Cancer_Type": "Lung"
        }
        resp = client.post("/api/predict", json=prediction_payload)
        assert resp.status_code == 200
        pred_data = resp.json()
        assert "prediction" in pred_data
        assert pred_data["prediction"] in ["Low", "Medium", "High"]
        assert "confidence_score" in pred_data
        assert "contributing_factors" in pred_data
        assert len(pred_data["contributing_factors"]) > 0
        assert "shap_value" in pred_data["contributing_factors"][0]
        assert isinstance(pred_data["contributing_factors"][0]["shap_value"], float)
        assert "explanation_narrative" in pred_data
        
        # 6. Test model prediction as authenticated user
        resp = client.post("/api/predict", json=prediction_payload, headers=headers)
        assert resp.status_code == 200
        
        # 7. Test history retrieval
        resp = client.get("/api/predictions/history", headers=headers)
        assert resp.status_code == 200
        history = resp.json()
        assert len(history) >= 1
        assert history[0]["patient_data"]["Age"] == 55
        
        # 8. Test analytics query as non-admin (should fail 403)
        resp = client.get("/api/predictions/analytics", headers=headers)
        assert resp.status_code == 403
        
        # 9a. Test admin retrain status retrieval as non-admin user (should fail 403)
        resp = client.get("/api/admin/retrain/status", headers=headers)
        assert resp.status_code == 403
        
        # 9b. Test triggering admin retraining as non-admin user (should fail 403)
        resp = client.post("/api/admin/retrain", headers=headers)
        assert resp.status_code == 403
        
        # 10. Promote test user to administrator in the database
        db_user = db.query(User).filter(User.email == test_email).first()
        db_user.is_admin = True
        db.commit()
        
        # 11a. Test admin retrain status retrieval as administrator (should succeed 200)
        resp = client.get("/api/admin/retrain/status", headers=headers)
        assert resp.status_code == 200
        status_data = resp.json()
        assert "is_training" in status_data
        assert "logs" in status_data
        assert isinstance(status_data["logs"], list)

        # 11b. Test analytics query as administrator (should succeed 200)
        resp = client.get("/api/predictions/analytics", headers=headers)
        assert resp.status_code == 200
        analytics = resp.json()
        assert analytics["total_assessments"] >= 1
        assert "risk_distribution" in analytics
        assert "trends" in analytics
        assert len(analytics["recent_runs"]) >= 1

        # 11c. Test triggering admin retraining as administrator (should succeed 202 or 409)
        resp = client.post("/api/admin/retrain", headers=headers)
        assert resp.status_code in [202, 409]

        # 12. Test incompatible gender/cancer combinations (should fail 422)
        incompatible_payload_male_breast = {
            **prediction_payload,
            "Gender": 1,
            "Cancer_Type": "Breast"
        }
        resp = client.post("/api/predict", json=incompatible_payload_male_breast)
        assert resp.status_code == 422

        incompatible_payload_female_prostate = {
            **prediction_payload,
            "Gender": 0,
            "Cancer_Type": "Prostate"
        }
        resp = client.post("/api/predict", json=incompatible_payload_female_prostate)
        assert resp.status_code == 422
        
    finally:
        # Cleanup test entries
        test_user = db.query(User).filter(User.email == test_email).first()
        if test_user:
            # Cascading delete handles prediction logs as well
            db.delete(test_user)
            db.commit()
        db.close()

if __name__ == "__main__":
    print("--- Starting API Integration Tests ---")
    try:
        print("[Step 1] Running test_health_check...")
        test_health_check()
        print("  Success: Health check working.")

        print("[Step 2] Running test_api_workflow...")
        test_api_workflow()
        print("  Success: Full API authentication, prediction, and analytics cycle working.")

        print("\nAll integration tests passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: Test validation failed! {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error during testing: {e}")
        sys.exit(1)
