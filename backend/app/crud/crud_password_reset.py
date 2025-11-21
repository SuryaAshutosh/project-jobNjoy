"""
CRUD operations for PasswordResetToken model
"""

from sqlalchemy.orm import Session
from app.models.db_models import PasswordResetToken, User
from datetime import datetime, timedelta
import uuid
import secrets

def create_password_reset_token(db: Session, user: User) -> PasswordResetToken:
    """Create a new password reset token for a user"""
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Set expiration time (24 hours from now)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    db_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    return db_token

def get_password_reset_token(db: Session, token: str) -> PasswordResetToken:
    """Get a password reset token by token value"""
    return db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

def mark_password_reset_token_as_used(db: Session, token: PasswordResetToken):
    """Mark a password reset token as used"""
    token.used = True
    db.commit()
    db.refresh(token)
    return token

def delete_expired_password_reset_tokens(db: Session):
    """Delete all expired password reset tokens"""
    expired_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.expires_at < datetime.utcnow()
    )
    count = expired_tokens.count()
    expired_tokens.delete()
    db.commit()
    return count