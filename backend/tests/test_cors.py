import os
import sys

# Ensure project root is in the Python path
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_cors_preflight_login():
    """
    Verify that OPTIONS preflight request to /api/auth/login succeeds
    from the new production frontend origin.
    """
    headers = {
        "Origin": "https://oncorisk-ai.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/auth/login", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://oncorisk-ai.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_cors_preflight_register():
    """
    Verify that OPTIONS preflight request to /api/auth/register succeeds
    from the new production frontend origin.
    """
    headers = {
        "Origin": "https://oncorisk-ai.vercel.app",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/auth/register", headers=headers)
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "https://oncorisk-ai.vercel.app"
    assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_preflight_authenticated_endpoints():
    """
    Verify that OPTIONS preflight request to other authenticated/endpoints succeeds
    from the new production frontend origin.
    """
    endpoints = ["/api/auth/me", "/api/predictions/history", "/api/predict"]
    for endpoint in endpoints:
        headers = {
            "Origin": "https://oncorisk-ai.vercel.app",
            "Access-Control-Request-Method": "GET" if endpoint != "/api/predict" else "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        }
        response = client.options(endpoint, headers=headers)
        assert response.status_code == 200, f"Failed for endpoint {endpoint}"
        assert response.headers.get("access-control-allow-origin") == "https://oncorisk-ai.vercel.app"
        assert response.headers.get("access-control-allow-credentials") == "true"

def test_cors_disallowed_origin():
    """
    Verify that OPTIONS preflight request from a disallowed origin is blocked
    and returns HTTP 400 (or doesn't include CORS approval headers).
    """
    headers = {
        "Origin": "https://untrusted-domain.com",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type",
    }
    response = client.options("/api/auth/login", headers=headers)
    # FastAPI/Starlette CORSMiddleware returns 400 response or a response lacking CORS headers when origin is not allowed
    # Let's assert either it returns HTTP 400 or lacks "access-control-allow-origin"
    assert response.status_code == 400 or "access-control-allow-origin" not in response.headers
