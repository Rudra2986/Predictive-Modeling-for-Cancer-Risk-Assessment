from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OncoRisk AI API",
    description="Predictive Modeling for Cancer Risk Assessment API Services",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "OncoRisk AI Backend"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
