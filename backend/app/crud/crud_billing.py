"""
CRUD operations for Billing model
"""

from sqlalchemy.orm import Session
from app.models.db_models import Billing
from app.schemas.schemas import BillingCreate, BillingUpdate
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

def get_billing_by_user(db: Session, user_id: UUID):
    """Get billing record by user ID"""
    return db.query(Billing).filter(Billing.user_id == user_id).first()

def get_billing_by_stripe_customer(db: Session, stripe_customer_id: str):
    """Get billing record by Stripe customer ID"""
    return db.query(Billing).filter(Billing.stripe_customer_id == stripe_customer_id).first()

def get_billing_by_stripe_subscription(db: Session, stripe_subscription_id: str):
    """Get billing record by Stripe subscription ID"""
    return db.query(Billing).filter(Billing.stripe_subscription_id == stripe_subscription_id).first()

def create_billing(db: Session, billing: BillingCreate):
    """Create a new billing record"""
    db_billing = Billing(**billing.dict())
    db.add(db_billing)
    db.commit()
    db.refresh(db_billing)
    return db_billing

def update_billing(db: Session, user_id: UUID, billing_update: BillingUpdate):
    """Update billing record"""
    db_billing = db.query(Billing).filter(Billing.user_id == user_id).first()
    if db_billing:
        update_data = billing_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_billing, key, value)
        db.commit()
        db.refresh(db_billing)
    return db_billing

def update_billing_by_stripe_subscription(db: Session, stripe_subscription_id: str, billing_update: BillingUpdate):
    """Update billing record by Stripe subscription ID"""
    db_billing = db.query(Billing).filter(Billing.stripe_subscription_id == stripe_subscription_id).first()
    if db_billing:
        update_data = billing_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_billing, key, value)
        db.commit()
        db.refresh(db_billing)
    return db_billing

def delete_billing(db: Session, user_id: UUID):
    """Delete billing record"""
    db_billing = db.query(Billing).filter(Billing.user_id == user_id).first()
    if db_billing:
        db.delete(db_billing)
        db.commit()
    return db_billing