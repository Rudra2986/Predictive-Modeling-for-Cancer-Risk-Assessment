from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Predictive Modeling for Cancer Risk Assessment API Services",
    version=settings.VERSION
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}
