import os
import sys
import pytest
import threading
import time
from fastapi.testclient import TestClient

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from backend.main import app
import backend.api.predict as predict
from backend.services.cache_service import cache_service

client = TestClient(app)

def test_model_readiness_handling():
    """
    Ensure the predict endpoint returns 503 while models are loading,
    and returns to normal function once loaded.
    """
    # Wait for model to be ready first
    for _ in range(50):
        with predict.model_loading_lock:
            if predict.model_ready:
                break
        time.sleep(0.1)

    # 1. Force state to not ready
    with predict.model_loading_lock:
        original_state = predict.model_ready
        predict.model_ready = False

    try:
        # Send a prediction request with a valid payload to bypass Pydantic validation
        valid_payload = {
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
        response = client.post("/api/predict", json=valid_payload)
        assert response.status_code == 503
        assert "ML model is currently initializing" in response.json()["detail"]
    finally:
        # Restore original state
        with predict.model_loading_lock:
            predict.model_ready = original_state

def test_cache_thread_safety():
    """
    Spawns multiple threads writing/reading from CacheService to ensure no race conditions/exceptions.
    """
    errors = []
    def worker(worker_id):
        try:
            for i in range(50):
                cache_service.set(f"q_{worker_id}_{i}", "hash", "MEDICAL_KNOWLEDGE", {"answer": f"a_{i}"})
                res = cache_service.get(f"q_{worker_id}_{i}", "hash", "MEDICAL_KNOWLEDGE")
                assert res == {"answer": f"a_{i}"}
                cache_service.clear()
        except Exception as e:
            errors.append(e)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0


def test_health_endpoint_metadata():
    """
    Verify the health check endpoint returns service metadata, database status, 
    and thread-safe model readiness.
    """
    # 1. Verify standard healthy response structure
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "OncoRisk AI"
    assert "database_connected" in data
    assert isinstance(data["database_connected"], bool)
    assert "model_ready" in data
    assert isinstance(data["model_ready"], bool)
    
    # 2. Simulate model loading/initializing state
    with predict.model_loading_lock:
        original_state = predict.model_ready
        predict.model_ready = False
        
    try:
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["model_ready"] is False
    finally:
        with predict.model_loading_lock:
            predict.model_ready = original_state
            
    # 3. Verify restore state works
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy" if original_state else "degraded"
    assert data["model_ready"] == original_state
