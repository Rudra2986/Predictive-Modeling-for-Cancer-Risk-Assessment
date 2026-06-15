from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "OncoRisk AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str = "local-development-secret-key-replace-in-production-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS Origins (comma separated in .env file)
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Database Configurations
    DATABASE_URL: str = "postgresql://postgres:postgres_secure_pass_2026@localhost:5432/oncorisk_db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
