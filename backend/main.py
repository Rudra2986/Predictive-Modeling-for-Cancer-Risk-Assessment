import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from backend.utils.config import settings
from backend.api import auth, predict, predictions, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("backend")

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

# Exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    logger.error(f"Validation error on {request.method} {request.url.path}: {errors}")
    
    # Sanitize errors to ensure they are JSON serializable (strip out raw exception objects in Pydantic v2 ctx)
    sanitized_errors = []
    for err in errors:
        err_dict = dict(err)
        if "ctx" in err_dict and isinstance(err_dict["ctx"], dict):
            ctx_clean = {}
            for k, v in err_dict["ctx"].items():
                if isinstance(v, Exception):
                    ctx_clean[k] = str(v)
                else:
                    ctx_clean[k] = v
            err_dict["ctx"] = ctx_clean
        sanitized_errors.append(err_dict)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": sanitized_errors, "message": "Request validation failed. Please check input parameters."}
    )

# Exception handler for standard HTTP Exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException on {request.method} {request.url.path}: [{exc.status_code}] {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# General unhandled exception handler
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error occurred. Please contact system support."}
    )

# Include API routers under the '/api' prefix
app.include_router(auth.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "healthy", "service": settings.PROJECT_NAME}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

