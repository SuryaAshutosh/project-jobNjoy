"""
Payments router for JobBuddy - Stripe integration
"""

import stripe
from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from app.db import get_db
from app.core.auth import get_current_active_user
from app.services.stripe_client import stripe_client
from app.crud.crud_user import update_user_subscription
from app.crud.crud_billing import get_billing_by_user
from app.models.db_models import User
from app.core.config import settings
from app.schemas.schemas import BillingResponse
import json
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

from pydantic import BaseModel

class CheckoutSessionRequest(BaseModel):
    """Request model for creating a checkout session"""
    plan_id: str
    success_url: str
    cancel_url: str
    trial_days: Optional[int] = None
    coupon: Optional[str] = None

class InvoicePaymentIntentRequest(BaseModel):
    """Request model for creating an invoice payment intent"""
    amount: int
    currency: str = "usd"
    description: str = ""

class CancelSubscriptionRequest(BaseModel):
    """Request model for canceling a subscription"""
    at_period_end: bool = True

@router.post("/create-checkout-session")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Stripe Checkout session for subscription
    
    Args:
        request: Checkout session request parameters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Checkout session details
    """
    try:
        checkout_session = stripe_client.create_checkout_session(
            db, current_user, request.plan_id, request.success_url, 
            request.cancel_url, request.trial_days, request.coupon
        )
        
        return checkout_session
    except Exception as e:
        logger.error(f"Failed to create checkout session for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create checkout session"
        )

@router.post("/create-portal-session")
async def create_portal_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a Stripe Customer Portal session for self-service billing management
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Portal session details
    """
    try:
        portal_session = stripe_client.create_portal_session(db, current_user)
        return portal_session
    except Exception as e:
        logger.error(f"Failed to create portal session for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create portal session"
        )

@router.post("/create-invoice-payment-intent")
async def create_invoice_payment_intent(
    request: InvoicePaymentIntentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a PaymentIntent for one-time purchases
    
    Args:
        request: Payment intent request parameters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Payment intent details
    """
    try:
        payment_intent = stripe_client.create_invoice_payment_intent(
            db, current_user, request.amount, request.currency, request.description
        )
        return payment_intent
    except Exception as e:
        logger.error(f"Failed to create payment intent for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create payment intent"
        )

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(...),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    
    Args:
        request: The incoming request
        stripe_signature: Stripe signature header
        db: Database session
        
    Returns:
        dict: Webhook response
    """
    # Get request body
    payload = await request.body()
    
    # Verify webhook signature
    event = stripe_client.verify_webhook_signature(
        payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
    )
    
    if not event:
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    # Process the event based on its type
    try:
        if event.type == "checkout.session.completed":
            # Handle successful checkout
            result = stripe_client.handle_checkout_session_completed(db, event.data.object)
            
        elif event.type == "invoice.paid":
            # Handle successful payment
            result = stripe_client.handle_invoice_paid(db, event.data.object)
            
        elif event.type == "invoice.payment_failed":
            # Handle failed payment
            result = stripe_client.handle_invoice_payment_failed(db, event.data.object)
            
        elif event.type == "customer.subscription.updated":
            # Handle subscription update
            result = stripe_client.handle_subscription_updated(db, event.data.object)
            
        elif event.type == "customer.subscription.deleted":
            # Handle subscription cancellation
            result = stripe_client.handle_subscription_deleted(db, event.data.object)
            
        elif event.type == "charge.refunded":
            # Handle refund
            logger.info(f"Charge refunded: {event.data.object.id}")
            result = {"status": "processed", "event_type": event.type}
            
        else:
            # Handle other events or ignore
            logger.info(f"Unhandled event type: {event.type}")
            result = {"status": "ignored", "event_type": event.type}
        
        return {"status": "success", "processed_event": result}
    except Exception as e:
        logger.error(f"Error processing webhook event {event.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook event"
        )

@router.get("/status")
async def get_payment_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current subscription status for logged-in user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Current subscription status
    """
    billing = get_billing_by_user(db, current_user.id)
    
    if not billing:
        return {
            "status": "no_subscription",
            "plan": "free",
            "subscription_status": "free"
        }
    
    return {
        "status": billing.status or "unknown",
        "plan": billing.plan or "free",
        "current_period_end": billing.current_period_end,
        "cancel_at_period_end": billing.cancel_at_period_end,
        "stripe_customer_id": billing.stripe_customer_id,
        "stripe_subscription_id": billing.stripe_subscription_id
    }

@router.post("/cancel-subscription")
async def cancel_subscription(
    request: CancelSubscriptionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel user's subscription
    
    Args:
        request: Cancellation request parameters
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Cancellation result
    """
    try:
        result = stripe_client.cancel_subscription(db, current_user, request.at_period_end)
        return result
    except Exception as e:
        logger.error(f"Failed to cancel subscription for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )

@router.post("/reactivate-subscription")
async def reactivate_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Reactivate user's canceled subscription
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        dict: Reactivation result
    """
    try:
        result = stripe_client.reactivate_subscription(db, current_user)
        return result
    except Exception as e:
        logger.error(f"Failed to reactivate subscription for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reactivate subscription"
        )

@router.get("/invoices")
async def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List invoices for the user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        list: List of invoices
    """
    # Get billing record to get Stripe customer ID
    billing = get_billing_by_user(db, current_user.id)
    
    if not billing or not billing.stripe_customer_id:
        return []
    
    try:
        # Retrieve invoices from Stripe
        invoices = stripe_client._retry_with_backoff(
            stripe.Invoice.list,
            customer=billing.stripe_customer_id,
            limit=100  # Limit to 100 most recent invoices
        )
        
        # Format invoices for response
        invoice_list = []
        for invoice in invoices.data:
            invoice_list.append({
                "id": invoice.id,
                "amount_due": invoice.amount_due,
                "amount_paid": invoice.amount_paid,
                "currency": invoice.currency,
                "status": invoice.status,
                "created": invoice.created,
                "period_start": invoice.period_start,
                "period_end": invoice.period_end,
                "hosted_invoice_url": invoice.hosted_invoice_url,
                "invoice_pdf": invoice.invoice_pdf,
                "subscription": invoice.subscription
            })
        
        return invoice_list
    except stripe.error.StripeError as e:
        logger.error(f"Failed to retrieve invoices for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )

@router.get("/billing", response_model=BillingResponse)
async def get_billing_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get billing information for the current user
    
    Args:
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        BillingResponse: User's billing information
    """
    billing = get_billing_by_user(db, current_user.id)
    
    if not billing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing information not found"
        )
    
    return billing