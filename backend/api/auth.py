from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime

from backend.database.session import get_db
from backend.services import user_service
from backend.utils import security
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic validation schemas
class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Plaintext password (min 8 characters with complexity)")

    @field_validator("password")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit.")
        return v

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginSchema(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreateSchema, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    try:
        new_user = user_service.register_user(db, email=user_in.email, password=user_in.password)
        return new_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenSchema)
def login_json(login_in: LoginSchema, db: Session = Depends(get_db)):
    """
    Authenticate user via JSON payload and retrieve JWT access token.
    """
    user = user_service.authenticate_user(db, email=login_in.email, password=login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/form", response_model=TokenSchema, include_in_schema=False)
def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Authenticate user via OAuth2 Form data (used by Swagger Authorize button).
    """
    user = user_service.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponseSchema)
def read_current_user(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user profile.
    """
    return current_user
