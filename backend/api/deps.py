from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from backend.database.session import get_db
from backend.models.user import User
from backend.services import user_service
from backend.utils.security import decode_access_token

# Token URL corresponds to the login endpoint (using the form route for Swagger support)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login/form", auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to fetch the currently authenticated user.
    Raises 401 Unauthorized if the token is missing, expired, or invalid.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    subject = decode_access_token(token)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(subject)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload structure",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    user = user_service.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
        
    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[User]:
    """
    Dependency to optionally fetch the authenticated user.
    Returns None if token is invalid, expired, or missing.
    """
    if not token:
        return None
    try:
        subject = decode_access_token(token)
        if not subject:
            return None
        user_id = int(subject)
        user = user_service.get_user_by_id(db, user_id=user_id)
        if user and user.is_active:
            return user
    except Exception:
        pass
    return None

def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to validate that the current user has administrative permissions.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have administrative privileges."
        )
    return current_user
