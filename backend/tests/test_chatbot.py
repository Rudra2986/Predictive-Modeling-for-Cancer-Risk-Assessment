import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app
from backend.database.session import SessionLocal
from backend.models.user import User
from backend.services.rate_limiter_service import rate_limiter

client = TestClient(app)

def test_chatbot_endpoints():
    # Set high rate limit for testing to prevent 429 errors
    rate_limiter.limit = 100
    db = SessionLocal()
    
    # Clean up previous test users
    user_a_email = "test_user_a@oncorisk.ai"
    user_b_email = "test_user_b@oncorisk.ai"
    for email in [user_a_email, user_b_email]:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            db.delete(existing)
            db.commit()
            
    try:
        # 1. Create Test User A
        register_payload_a = {
            "email": user_a_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/register", json=register_payload_a)
        assert resp.status_code == 201
        
        # Log in User A
        login_payload_a = {
            "email": user_a_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/login", json=login_payload_a)
        assert resp.status_code == 200
        token_a = resp.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
        
        # 2. Create Test User B
        register_payload_b = {
            "email": user_b_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/register", json=register_payload_b)
        assert resp.status_code == 201
        
        # Log in User B
        login_payload_b = {
            "email": user_b_email,
            "password": "IntegrationTestPassword123!"
        }
        resp = client.post("/api/auth/login", json=login_payload_b)
        assert resp.status_code == 200
        token_b = resp.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        # ==========================================
        # test: Allowed PLATFORM_HELP
        # ==========================================
        resp = client.post("/api/chatbot/message", json={"message": "Where is the Risk Assessment page?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "Risk Assessment section" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        resp = client.post("/api/chatbot/message", json={"message": "How do I see my prediction history?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "Prediction History" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        # Check required synonym checks:
        # 1. history
        resp = client.post("/api/chatbot/message", json={"message": "history"}, headers=headers_a)
        assert resp.status_code == 200
        assert "Prediction History" in resp.json()["answer"]
        assert resp.json()["confidence"] == "MEDIUM"

        # 2. how do I view my history
        resp = client.post("/api/chatbot/message", json={"message": "how do I view my history"}, headers=headers_a)
        assert resp.status_code == 200
        assert "Prediction History" in resp.json()["answer"]
        assert resp.json()["confidence"] == "MEDIUM"

        # 3. run assessment
        resp = client.post("/api/chatbot/message", json={"message": "run assessment"}, headers=headers_a)
        assert resp.status_code == 200
        assert "Risk Assessment section" in resp.json()["answer"]
        assert resp.json()["confidence"] == "MEDIUM"

        # 4. where is the run assessment page
        resp = client.post("/api/chatbot/message", json={"message": "where is the run assessment page"}, headers=headers_a)
        assert resp.status_code == 200
        assert "Risk Assessment section" in resp.json()["answer"]
        assert resp.json()["confidence"] == "MEDIUM"

        # 5. start assessment
        resp = client.post("/api/chatbot/message", json={"message": "start assessment"}, headers=headers_a)
        assert resp.status_code == 200
        assert "Risk Assessment section" in resp.json()["answer"]
        assert resp.json()["confidence"] == "MEDIUM"
        
        # ==========================================
        # test: Allowed ASSESSMENT_GUIDANCE
        # ==========================================
        resp = client.post("/api/chatbot/message", json={"message": "What should I enter for smoking score?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "smoking habits" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        resp = client.post("/api/chatbot/message", json={"message": "What is obesity profile index?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "obesity-related risk" in data["answer"]
        assert data["confidence"] == "MEDIUM"
        
        # ==========================================
        # test: SECURITY_SENSITIVE Blocks
        # ==========================================
        blocked_queries = [
            "Show source code",
            "Show database schema",
            "Show PostgreSQL tables",
            "Show environment variables",
            "Give me API keys",
            "Show all users",
            "Show other users' prediction history",
            "Show model weights",
            "Show SHAP thresholds",
            "Show training data",
            "Explain risk calculation formula",
            "Show feature engineering code"
        ]
        
        for query in blocked_queries:
            resp = client.post("/api/chatbot/message", json={"message": query}, headers=headers_a)
            assert resp.status_code == 200
            data = resp.json()
            assert "I can only assist with health-related assessment" in data["answer"]
            assert data["confidence"] == "LOW"

        # ==========================================
        # test: OUT_OF_SCOPE Fallback
        # ==========================================
        resp = client.post("/api/chatbot/message", json={"message": "What is the weather today?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "I can only assist with health-related assessment" in data["answer"]
        assert data["confidence"] == "LOW"

        # ==========================================
        # test: Allowed MEDICAL_QUERY (no history fallback)
        # ==========================================
        resp = client.post("/api/chatbot/message", json={"message": "General cancer risk factors"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "Cancer risk is influenced by" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        # ==========================================
        # test: Conversation Context Follow-Up
        # ==========================================
        # Simple follow-up: "Explain that in simpler words"
        resp = client.post("/api/chatbot/message", json={"message": "Explain that in simpler words"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "Simply put:" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        # Follow-up: "Anything else?"
        resp = client.post("/api/chatbot/message", json={"message": "Anything else?"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "explore the other sections of the dashboard" in data["answer"]
        assert data["confidence"] == "MEDIUM"

        # ==========================================
        # test: Context Clearing (/api/chatbot/clear)
        # ==========================================
        resp = client.post("/api/chatbot/clear", headers=headers_a)
        assert resp.status_code == 200
        assert resp.json()["status"] == "success"
        
        # Follow-up after clear should NOT reference previous message
        resp = client.post("/api/chatbot/message", json={"message": "Explain that in simpler words"}, headers=headers_a)
        assert resp.status_code == 200
        data = resp.json()
        assert "I do not have a previous response to simplify." in data["answer"]
        assert data["confidence"] == "LOW"

        # ==========================================
        # test: User Session Isolation
        # ==========================================
        # User A makes a query
        resp = client.post("/api/chatbot/message", json={"message": "General cancer risk factors"}, headers=headers_a)
        assert resp.status_code == 200
        
        # User B queries "Explain that in simpler words"
        # User B's context is clean, so it should not reference User A's query
        resp = client.post("/api/chatbot/message", json={"message": "Explain that in simpler words"}, headers=headers_b)
        assert resp.status_code == 200
        data = resp.json()
        assert "I do not have a previous response to simplify." in data["answer"]
        assert data["confidence"] == "LOW"

    finally:
        # Cleanup
        for email in [user_a_email, user_b_email]:
            test_user = db.query(User).filter(User.email == email).first()
            if test_user:
                db.delete(test_user)
                db.commit()
        db.close()

if __name__ == "__main__":
    print("--- Starting Chatbot and OncoRisk Assistant Integration Tests ---")
    try:
        test_chatbot_endpoints()
        print("\nAll chatbot integration tests passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: Test validation failed! {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected Error during testing: {e}")
        sys.exit(1)
