from typing import List, Any, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "OncoRisk AI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security Configuration
    SECRET_KEY: str = "local-development-secret-key-replace-in-production-12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS Origins (comma separated in .env file)
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000", "https://oncorisk-ai.vercel.app"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            v_clean = v.strip()
            if v_clean.startswith("[") and v_clean.endswith("]"):
                try:
                    import json
                    parsed = json.loads(v_clean)
                    if isinstance(parsed, list):
                        return [str(i).strip() for i in parsed]
                except Exception:
                    pass
            return [i.strip() for i in v_clean.split(",") if i.strip()]
        elif isinstance(v, list):
            return [str(i).strip() for i in v]
        raise ValueError(f"Invalid CORS origins format: {v}")

    @field_validator("BACKEND_CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        if "*" in v:
            raise ValueError("CORS origins cannot contain wildcard '*' because credential support is enabled.")
        return v
    
    # Database Configurations
    DATABASE_URL: str = "sqlite:///oncorisk.db"

    # Chatbot Configurations
    APPEND_DISCLAIMER_TO_MESSAGES: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_security_settings(self) -> "Settings":
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "local-development-secret-key-replace-in-production-12345":
                raise ValueError("SECRET_KEY must be changed from the default development key when running in production mode.")
            if len(self.SECRET_KEY) < 32:
                raise ValueError("SECRET_KEY must be at least 32 characters long for production mode security.")
            if "postgres_secure_pass_2026" in self.DATABASE_URL:
                raise ValueError("DATABASE_URL must not use the default development password in production mode.")
            if "localhost" in self.DATABASE_URL:
                raise ValueError("DATABASE_URL must not point to localhost in production mode (use a secure production host).")
        return self

settings = Settings()
