"""
Authentication router for JobBuddy
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.schemas import UserCreate, UserResponse, UserLogin
from app.crud.crud_user import create_user, get_user_by_email, update_user
from app.crud.crud_password_reset import create_password_reset_token, get_password_reset_token, mark_password_reset_token_as_used, delete_expired_password_reset_tokens
from app.core.auth import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from app.core.config import settings
from app.services.email_service import email_service

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Args:
        user: User registration data
        db: Database session
        
    Returns:
        UserResponse: The created user
    """
    # Check if user already exists
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = create_user(db, user)
    return new_user

@router.post("/login")
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token
    
    Args:
        login_data: Login data (email and password)
        db: Database session
        
    Returns:
        dict: Access token and token type
    """
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "subscription_status": user.subscription_status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None
        }
    }

@router.post("/forgot-password")
async def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    """
    Handle forgot password request
    
    Args:
        email: User's email address
        db: Database session
        
    Returns:
        dict: Success message
    """
    # Delete expired tokens first
    delete_expired_password_reset_tokens(db)
    
    # Check if user exists
    user = get_user_by_email(db, email=email)
    if not user:
        # We don't reveal if the email exists for security reasons
        return {"message": "If the email exists in our system, password reset instructions have been sent."}
    
    # Create a new password reset token
    reset_token = create_password_reset_token(db, user)
    
    # Send email with reset link
    email_sent = email_service.send_password_reset_email(user.email, reset_token.token, user.name)
    
    if not email_sent:
        # Log the error but don't reveal it to the user
        print(f"Failed to send password reset email to {user.email}")
    
    return {"message": "If the email exists in our system, password reset instructions have been sent."}

@router.post("/reset-password")
async def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Reset user password with token
    
    Args:
        token: Password reset token
        new_password: New password
        db: Database session
        
    Returns:
        dict: Success message
    """
    # Delete expired tokens first
    delete_expired_password_reset_tokens(db)
    
    # Validate the token
    reset_token = get_password_reset_token(db, token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    from datetime import datetime
    if reset_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Check if token has already been used
    if reset_token.used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has already been used"
        )
    
    # Hash the new password
    hashed_password = get_password_hash(new_password)
    
    # Update the user's password
    reset_token.user.password_hash = hashed_password
    db.commit()
    
    # Mark token as used
    mark_password_reset_token_as_used(db, reset_token)
    
    return {"message": "Password has been reset successfully."}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_active_user)):
    """
    Get current user profile
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Current user profile
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Update current user profile
    
    Args:
        user_update: User profile update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        UserResponse: Updated user profile
    """
    try:
        updated_user = update_user(db, str(current_user.id), user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )