"""
Stripe client service for JobBuddy
"""

import stripe
import os
import time
import logging
from typing import Dict, Any, Optional, Union
from fastapi import HTTPException, status
from app.core.config import settings
from app.models.db_models import User
from app.schemas.schemas import BillingCreate, BillingUpdate
from app.crud.crud_billing import get_billing_by_user, create_billing, update_billing, get_billing_by_stripe_customer, update_billing_by_stripe_subscription
from sqlalchemy.orm import Session

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

# Set up logging
logger = logging.getLogger(__name__)

# Plan configuration mapping
STRIPE_PLANS = {
    "basic": {
        "price_id": os.getenv("STRIPE_PRICE_BASIC"),
        "trial_days": int(os.getenv("STRIPE_TRIAL_DAYS_BASIC", "0"))
    },
    "pro": {
        "price_id": os.getenv("STRIPE_PRICE_PRO"),
        "trial_days": int(os.getenv("STRIPE_TRIAL_DAYS_PRO", "0"))
    },
    "unlimited": {
        "price_id": os.getenv("STRIPE_PRICE_UNLIMITED"),
        "trial_days": int(os.getenv("STRIPE_TRIAL_DAYS_UNLIMITED", "0"))
    }
}

class StripeClient:
    """Service for handling Stripe operations"""
    
    def __init__(self):
        """Initialize the Stripe client"""
        self.stripe = stripe
        self.stripe.api_key = settings.STRIPE_SECRET_KEY
        # Set API version if provided
        if hasattr(settings, 'STRIPE_API_VERSION') and settings.STRIPE_API_VERSION:
            self.stripe.api_version = settings.STRIPE_API_VERSION
    
    def _retry_with_backoff(self, func, *args, max_retries=3, **kwargs):
        """
        Retry a Stripe API call with exponential backoff
        
        Args:
            func: The Stripe API function to call
            *args: Positional arguments for the function
            max_retries: Maximum number of retry attempts
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the Stripe API call
        """
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except stripe.error.RateLimitError:
                if attempt == max_retries - 1:
                    raise
                # Wait for 2^attempt seconds before retrying
                time.sleep(2 ** attempt)
            except stripe.error.APIConnectionError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
            except stripe.error.APIError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
    
    def ensure_stripe_customer(self, db: Session, user: User) -> str:
        """
        Ensure a Stripe customer exists for the user
        
        Args:
            db: Database session
            user: The user object
            
        Returns:
            str: Stripe customer ID
        """
        # Check if user already has a billing record with a Stripe customer ID
        billing = get_billing_by_user(db, user.id)
        
        if billing and billing.stripe_customer_id:
            return billing.stripe_customer_id
        
        # Create a new Stripe customer
        try:
            customer = self._retry_with_backoff(
                self.stripe.Customer.create,
                email=user.email,
                name=user.name,
                metadata={
                    "user_id": str(user.id),
                    "created_via": "jobsee_platform"
                }
            )
            
            # Create or update billing record
            if billing:
                billing_update = BillingUpdate(stripe_customer_id=customer.id)
                update_billing(db, user.id, billing_update)
            else:
                billing_create = BillingCreate(
                    user_id=user.id,
                    stripe_customer_id=customer.id
                )
                create_billing(db, billing_create)
            
            return customer.id
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create customer account"
            )
    
    def create_checkout_session(
        self, 
        db: Session, 
        user: User, 
        plan_id: str, 
        success_url: str, 
        cancel_url: str, 
        trial_days: Optional[int] = None,
        coupon: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a Stripe Checkout session
        
        Args:
            db: Database session
            user: The user object
            plan_id: The plan identifier (basic, pro, unlimited)
            success_url: URL to redirect to after successful payment
            cancel_url: URL to redirect to after cancelled payment
            trial_days: Number of trial days (optional)
            coupon: Coupon code (optional)
            
        Returns:
            Dict: Checkout session details
        """
        # Validate plan
        if plan_id not in STRIPE_PLANS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid plan: {plan_id}"
            )
        
        # Get price ID and trial days from config
        plan_config = STRIPE_PLANS[plan_id]
        price_id = plan_config["price_id"]
        default_trial_days = plan_config["trial_days"]
        
        # Use provided trial days or default from config
        actual_trial_days = trial_days if trial_days is not None else default_trial_days
        
        # Ensure Stripe customer exists
        customer_id = self.ensure_stripe_customer(db, user)
        
        # Prepare checkout session parameters
        checkout_params = {
            "mode": "subscription",
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": str(user.id),
            "customer": customer_id,
            "automatic_tax": {"enabled": True} if os.getenv("STRIPE_TAX_ENABLED", "false").lower() == "true" else {"enabled": False}
        }
        
        # Add trial period if applicable
        if actual_trial_days > 0:
            checkout_params["subscription_data"] = {
                "trial_period_days": actual_trial_days
            }
        
        # Add coupon if provided
        if coupon:
            checkout_params["discounts"] = [{"coupon": coupon}]
        
        try:
            checkout_session = self._retry_with_backoff(
                self.stripe.checkout.Session.create,
                **checkout_params
            )
            
            return {
                "id": checkout_session.id,
                "url": checkout_session.url,
                "status": checkout_session.status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create checkout session: {str(e)}"
            )
    
    def create_portal_session(self, db: Session, user: User) -> Dict[str, Any]:
        """
        Create a Stripe Customer Portal session
        
        Args:
            db: Database session
            user: The user object
            
        Returns:
            Dict: Portal session details
        """
        # Ensure Stripe customer exists
        customer_id = self.ensure_stripe_customer(db, user)
        
        try:
            portal_session = self._retry_with_backoff(
                self.stripe.billing_portal.Session.create,
                customer=customer_id,
                return_url=os.getenv("STRIPE_PORTAL_RETURN_URL", success_url)
            )
            
            return {
                "url": portal_session.url
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create portal session: {str(e)}"
            )
    
    def create_invoice_payment_intent(self, db: Session, user: User, amount: int, currency: str = "usd", description: str = "") -> Dict[str, Any]:
        """
        Create a PaymentIntent for a one-time purchase
        
        Args:
            db: Database session
            user: The user object
            amount: Amount in cents
            currency: Currency code (default: USD)
            description: Description of the charge
            
        Returns:
            Dict: PaymentIntent details
        """
        # Ensure Stripe customer exists
        customer_id = self.ensure_stripe_customer(db, user)
        
        try:
            payment_intent = self._retry_with_backoff(
                self.stripe.PaymentIntent.create,
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
                automatic_payment_methods={"enabled": True}
            )
            
            return {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                "status": payment_intent.status
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create payment intent for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create payment intent: {str(e)}"
            )
    
    def cancel_subscription(self, db: Session, user: User, at_period_end: bool = True) -> Dict[str, Any]:
        """
        Cancel a user's subscription
        
        Args:
            db: Database session
            user: The user object
            at_period_end: Whether to cancel at period end (True) or immediately (False)
            
        Returns:
            Dict: Cancellation result
        """
        # Get billing record
        billing = get_billing_by_user(db, user.id)
        
        if not billing or not billing.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active subscription found"
            )
        
        try:
            # Retrieve subscription to get current status
            subscription = self._retry_with_backoff(
                self.stripe.Subscription.retrieve,
                billing.stripe_subscription_id
            )
            
            # Check if already canceled
            if subscription.cancel_at_period_end or subscription.status in ["canceled", "unpaid"]:
                return {
                    "status": "already_canceled",
                    "subscription_id": subscription.id,
                    "cancel_at_period_end": subscription.cancel_at_period_end,
                    "current_period_end": subscription.current_period_end
                }
            
            # Cancel subscription
            if at_period_end:
                updated_subscription = self._retry_with_backoff(
                    self.stripe.Subscription.modify,
                    billing.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                
                # Update billing record
                billing_update = BillingUpdate(cancel_at_period_end=True)
                update_billing(db, user.id, billing_update)
                
                return {
                    "status": "scheduled_for_cancellation",
                    "subscription_id": updated_subscription.id,
                    "cancel_at_period_end": updated_subscription.cancel_at_period_end,
                    "current_period_end": updated_subscription.current_period_end
                }
            else:
                canceled_subscription = self._retry_with_backoff(
                    self.stripe.Subscription.delete,
                    billing.stripe_subscription_id
                )
                
                # Update billing record
                billing_update = BillingUpdate(
                    status="canceled",
                    cancel_at_period_end=False
                )
                update_billing(db, user.id, billing_update)
                
                return {
                    "status": "canceled",
                    "subscription_id": canceled_subscription.id
                }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel subscription: {str(e)}"
            )
    
    def reactivate_subscription(self, db: Session, user: User) -> Dict[str, Any]:
        """
        Reactivate a user's canceled subscription
        
        Args:
            db: Database session
            user: The user object
            
        Returns:
            Dict: Reactivation result
        """
        # Get billing record
        billing = get_billing_by_user(db, user.id)
        
        if not billing or not billing.stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No subscription found"
            )
        
        try:
            # Retrieve subscription to get current status
            subscription = self._retry_with_backoff(
                self.stripe.Subscription.retrieve,
                billing.stripe_subscription_id
            )
            
            # Check if can be reactivated
            if subscription.status not in ["active", "trialing"] and subscription.cancel_at_period_end:
                # Reactivate subscription
                updated_subscription = self._retry_with_backoff(
                    self.stripe.Subscription.modify,
                    billing.stripe_subscription_id,
                    cancel_at_period_end=False
                )
                
                # Update billing record
                billing_update = BillingUpdate(cancel_at_period_end=False)
                update_billing(db, user.id, billing_update)
                
                return {
                    "status": "reactivated",
                    "subscription_id": updated_subscription.id,
                    "cancel_at_period_end": updated_subscription.cancel_at_period_end
                }
            elif subscription.status in ["active", "trialing"]:
                return {
                    "status": "already_active",
                    "subscription_id": subscription.id
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Subscription cannot be reactivated"
                )
        except stripe.error.StripeError as e:
            logger.error(f"Failed to reactivate subscription for user {user.id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to reactivate subscription: {str(e)}"
            )
    
    def sync_subscription_status(self, db: Session, stripe_subscription_id: str) -> Dict[str, Any]:
        """
        Sync subscription status from Stripe to local database
        
        Args:
            db: Database session
            stripe_subscription_id: Stripe subscription ID
            
        Returns:
            Dict: Sync result
        """
        try:
            # Retrieve subscription from Stripe
            subscription = self._retry_with_backoff(
                self.stripe.Subscription.retrieve,
                stripe_subscription_id
            )
            
            # Update billing record
            billing_update = BillingUpdate(
                plan=subscription.items.data[0].price.lookup_key if subscription.items.data[0].price.lookup_key else subscription.items.data[0].price.id,
                status=subscription.status,
                current_period_start=subscription.current_period_start,
                current_period_end=subscription.current_period_end,
                cancel_at_period_end=subscription.cancel_at_period_end,
                metadata={"stripe_subscription": subscription.to_dict_recursive()}
            )
            
            updated_billing = update_billing_by_stripe_subscription(db, stripe_subscription_id, billing_update)
            
            return {
                "status": "synced",
                "subscription_id": subscription.id,
                "billing_id": updated_billing.id if updated_billing else None
            }
        except stripe.error.StripeError as e:
            logger.error(f"Failed to sync subscription {stripe_subscription_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to sync subscription: {str(e)}"
            )
    
    def verify_webhook_signature(self, payload: bytes, sig_header: str, webhook_secret: str) -> Optional[stripe.Event]:
        """
        Verify the signature of a Stripe webhook
        
        Args:
            payload: The webhook payload
            sig_header: The signature header from the request
            webhook_secret: The webhook secret
            
        Returns:
            stripe.Event: The verified event, or None if verification fails
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            return event
        except ValueError:
            # Invalid payload
            logger.warning("Invalid webhook payload")
            return None
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            logger.warning("Invalid webhook signature")
            return None
    
    def handle_checkout_session_completed(self, db: Session, session: stripe.checkout.Session) -> Dict[str, Any]:
        """
        Handle a checkout.session.completed event
        
        Args:
            db: Database session
            session: The Stripe checkout session object
            
        Returns:
            Dict: Processing result
        """
        try:
            # Retrieve the subscription if it's a subscription mode
            if session.mode == "subscription":
                subscription = self._retry_with_backoff(
                    self.stripe.Subscription.retrieve,
                    session.subscription
                )
                
                # Get user ID from client reference
                user_id = session.client_reference_id
                
                # Get or create billing record
                billing = get_billing_by_user(db, user_id)
                
                # Update billing information
                billing_update = BillingUpdate(
                    stripe_subscription_id=subscription.id,
                    plan=subscription.items.data[0].price.lookup_key if subscription.items.data[0].price.lookup_key else "unknown",
                    status=subscription.status,
                    current_period_start=subscription.current_period_start,
                    current_period_end=subscription.current_period_end,
                    cancel_at_period_end=subscription.cancel_at_period_end
                )
                
                if billing:
                    update_billing(db, user_id, billing_update)
                else:
                    # Create new billing record
                    billing_create = BillingCreate(
                        user_id=user_id,
                        stripe_customer_id=session.customer,
                        stripe_subscription_id=subscription.id,
                        plan=subscription.items.data[0].price.lookup_key if subscription.items.data[0].price.lookup_key else "unknown",
                        status=subscription.status,
                        current_period_start=subscription.current_period_start,
                        current_period_end=subscription.current_period_end,
                        cancel_at_period_end=subscription.cancel_at_period_end
                    )
                    create_billing(db, billing_create)
                
                logger.info(f"Subscription activated for user {user_id}: {subscription.id}")
                
                return {
                    "status": "processed",
                    "subscription_id": subscription.id,
                    "customer_id": session.customer,
                    "user_id": user_id
                }
            else:
                logger.info(f"Checkout session completed for one-time payment: {session.id}")
                return {
                    "status": "processed",
                    "session_id": session.id,
                    "customer_id": session.customer
                }
        except Exception as e:
            logger.error(f"Error handling checkout session completed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_invoice_paid(self, db: Session, invoice: stripe.Invoice) -> Dict[str, Any]:
        """
        Handle an invoice.paid event
        
        Args:
            db: Database session
            invoice: The Stripe invoice object
            
        Returns:
            Dict: Processing result
        """
        try:
            # Get billing record by Stripe customer ID
            billing = get_billing_by_stripe_customer(db, invoice.customer)
            
            if billing and billing.stripe_subscription_id == invoice.subscription:
                # Update billing record
                billing_update = BillingUpdate(
                    status="active",
                    current_period_end=invoice.period_end
                )
                update_billing(db, billing.user_id, billing_update)
                
                logger.info(f"Invoice paid for subscription {invoice.subscription}: {invoice.id}")
                
                return {
                    "status": "processed",
                    "invoice_id": invoice.id,
                    "subscription_id": invoice.subscription,
                    "customer_id": invoice.customer
                }
            else:
                logger.info(f"Invoice paid for one-time payment: {invoice.id}")
                return {
                    "status": "processed",
                    "invoice_id": invoice.id,
                    "customer_id": invoice.customer
                }
        except Exception as e:
            logger.error(f"Error handling invoice paid: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_invoice_payment_failed(self, db: Session, invoice: stripe.Invoice) -> Dict[str, Any]:
        """
        Handle an invoice.payment_failed event
        
        Args:
            db: Database session
            invoice: The Stripe invoice object
            
        Returns:
            Dict: Processing result
        """
        try:
            # Get billing record by Stripe customer ID
            billing = get_billing_by_stripe_customer(db, invoice.customer)
            
            if billing and billing.stripe_subscription_id == invoice.subscription:
                # Update billing record
                billing_update = BillingUpdate(status="past_due")
                update_billing(db, billing.user_id, billing_update)
                
                logger.warning(f"Invoice payment failed for subscription {invoice.subscription}: {invoice.id}")
                
                return {
                    "status": "processed",
                    "invoice_id": invoice.id,
                    "subscription_id": invoice.subscription,
                    "customer_id": invoice.customer
                }
            else:
                logger.warning(f"Invoice payment failed for one-time payment: {invoice.id}")
                return {
                    "status": "processed",
                    "invoice_id": invoice.id,
                    "customer_id": invoice.customer
                }
        except Exception as e:
            logger.error(f"Error handling invoice payment failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_subscription_updated(self, db: Session, subscription: stripe.Subscription) -> Dict[str, Any]:
        """
        Handle a subscription.updated event
        
        Args:
            db: Database session
            subscription: The Stripe subscription object
            
        Returns:
            Dict: Processing result
        """
        try:
            # Get billing record by Stripe subscription ID
            billing = get_billing_by_stripe_subscription(db, subscription.id)
            
            if billing:
                # Update billing record
                billing_update = BillingUpdate(
                    plan=subscription.items.data[0].price.lookup_key if subscription.items.data[0].price.lookup_key else "unknown",
                    status=subscription.status,
                    current_period_start=subscription.current_period_start,
                    current_period_end=subscription.current_period_end,
                    cancel_at_period_end=subscription.cancel_at_period_end
                )
                update_billing(db, billing.user_id, billing_update)
                
                logger.info(f"Subscription updated: {subscription.id}")
                
                return {
                    "status": "processed",
                    "subscription_id": subscription.id,
                    "customer_id": subscription.customer
                }
            else:
                logger.warning(f"Subscription updated but no local billing record found: {subscription.id}")
                return {
                    "status": "warning",
                    "message": "Subscription updated but no local billing record found",
                    "subscription_id": subscription.id,
                    "customer_id": subscription.customer
                }
        except Exception as e:
            logger.error(f"Error handling subscription updated: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def handle_subscription_deleted(self, db: Session, subscription: stripe.Subscription) -> Dict[str, Any]:
        """
        Handle a subscription.deleted event
        
        Args:
            db: Database session
            subscription: The Stripe subscription object
            
        Returns:
            Dict: Processing result
        """
        try:
            # Get billing record by Stripe subscription ID
            billing = get_billing_by_stripe_subscription(db, subscription.id)
            
            if billing:
                # Update billing record
                billing_update = BillingUpdate(
                    status="canceled",
                    cancel_at_period_end=False
                )
                update_billing(db, billing.user_id, billing_update)
                
                logger.info(f"Subscription deleted: {subscription.id}")
                
                return {
                    "status": "processed",
                    "subscription_id": subscription.id,
                    "customer_id": subscription.customer
                }
            else:
                logger.warning(f"Subscription deleted but no local billing record found: {subscription.id}")
                return {
                    "status": "warning",
                    "message": "Subscription deleted but no local billing record found",
                    "subscription_id": subscription.id,
                    "customer_id": subscription.customer
                }
        except Exception as e:
            logger.error(f"Error handling subscription deleted: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global Stripe client instance
stripe_client = StripeClient()