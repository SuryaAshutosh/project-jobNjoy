"""
CRUD operations for User model
"""

from sqlalchemy.orm import Session
from app.models.db_models import User
from app.schemas.schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: str):
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get multiple users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user"""
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password"""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not pwd_context.verify(password, user.password_hash):
        return False
    return user

def update_user_subscription(db: Session, user_id: str, subscription_status: str):
    """Update user's subscription status"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db_user.subscription_status = subscription_status
        db.commit()
        db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user_update):
    """Update user profile information"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        if hasattr(user_update, 'name') and user_update.name:
            db_user.name = user_update.name
        if hasattr(user_update, 'email') and user_update.email:
            # Check if email is already taken by another user
            existing_user = get_user_by_email(db, user_update.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("Email already registered")
            db_user.email = user_update.email
        db.commit()
        db.refresh(db_user)
    return db_user
