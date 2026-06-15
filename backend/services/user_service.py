from sqlalchemy.orm import Session
from backend.models.user import User
from backend.utils.security import hash_password, verify_password

def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieves a user account by email address.
    """
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User:
    """
    Retrieves a user account by primary key ID.
    """
    return db.query(User).filter(User.id == user_id).first()

def register_user(db: Session, email: str, password: str) -> User:
    """
    Registers a new user account after hashing their password.
    Raises ValueError if email is already taken.
    """
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise ValueError("A user account with this email already exists.")
        
    hashed_pwd = hash_password(password)
    new_user = User(
        email=email,
        hashed_password=hashed_pwd
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticates a user account by email and plain password.
    Returns the User model instance if valid, otherwise None.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
