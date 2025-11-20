#!/usr/bin/env python3
"""
Admin script for syncing Stripe data with local database
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any
import stripe
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.core.config import settings
from app.models.db_models import Billing, User
from app.schemas.schemas import BillingCreate
from app.crud.crud_billing import create_billing, update_billing_by_stripe_subscription

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_session():
    """Create and return a database session"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def sync_customers():
    """Sync all Stripe customers with local database"""
    logger.info("Starting customer sync...")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    db = get_db_session()
    
    try:
        # List all customers from Stripe
        customers = stripe.Customer.list(limit=100)  # Adjust limit as needed
        
        synced_count = 0
        for customer in customers.auto_paging_iter():
            try:
                # Check if customer already exists in our database
                existing_billing = db.query(Billing).filter(
                    Billing.stripe_customer_id == customer.id
                ).first()
                
                if not existing_billing:
                    # Create new billing record
                    # Try to find user by email
                    user = db.query(User).filter(User.email == customer.email).first()
                    
                    if user:
                        billing_create = BillingCreate(
                            user_id=user.id,
                            stripe_customer_id=customer.id,
                            metadata={"customer_data": customer.to_dict_recursive()}
                        )
                        create_billing(db, billing_create)
                        synced_count += 1
                        logger.info(f"Created billing record for customer {customer.id}")
                    else:
                        logger.warning(f"No user found for customer email {customer.email}")
                else:
                    logger.info(f"Customer {customer.id} already exists in database")
                    
            except Exception as e:
                logger.error(f"Error processing customer {customer.id}: {str(e)}")
                continue
        
        logger.info(f"Synced {synced_count} new customers")
        
    except Exception as e:
        logger.error(f"Error during customer sync: {str(e)}")
    finally:
        db.close()

def sync_subscriptions():
    """Sync all Stripe subscriptions with local database"""
    logger.info("Starting subscription sync...")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    db = get_db_session()
    
    try:
        # List all subscriptions from Stripe
        subscriptions = stripe.Subscription.list(limit=100, status="all")  # Get all statuses
        
        synced_count = 0
        for subscription in subscriptions.auto_paging_iter():
            try:
                # Update or create billing record based on subscription
                billing_update = {
                    "stripe_subscription_id": subscription.id,
                    "plan": subscription.items.data[0].price.lookup_key if subscription.items.data[0].price.lookup_key else subscription.items.data[0].price.id,
                    "status": subscription.status,
                    "current_period_start": subscription.current_period_start,
                    "current_period_end": subscription.current_period_end,
                    "cancel_at_period_end": subscription.cancel_at_period_end,
                    "metadata": {"stripe_subscription": subscription.to_dict_recursive()}
                }
                
                # Update billing record by Stripe subscription ID
                updated_billing = update_billing_by_stripe_subscription(
                    db, subscription.id, billing_update
                )
                
                if updated_billing:
                    synced_count += 1
                    logger.info(f"Updated billing record for subscription {subscription.id}")
                else:
                    logger.warning(f"No billing record found for subscription {subscription.id}")
                    
            except Exception as e:
                logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
                continue
        
        logger.info(f"Synced {synced_count} subscriptions")
        
    except Exception as e:
        logger.error(f"Error during subscription sync: {str(e)}")
    finally:
        db.close()

def create_coupon(name: str, duration: str, amount_off: int = None, percent_off: int = None, currency: str = None, max_redemptions: int = None):
    """Create a promotional coupon in Stripe"""
    logger.info(f"Creating coupon: {name}")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        coupon_params = {
            "name": name,
            "duration": duration,  # once, forever, repeating
        }
        
        if amount_off is not None:
            coupon_params["amount_off"] = amount_off
            coupon_params["currency"] = currency
        elif percent_off is not None:
            coupon_params["percent_off"] = percent_off
        else:
            raise ValueError("Either amount_off or percent_off must be specified")
        
        if max_redemptions is not None:
            coupon_params["max_redemptions"] = max_redemptions
            
        if duration == "repeating":
            # Default to 3 months for repeating coupons
            coupon_params["duration_in_months"] = 3
        
        coupon = stripe.Coupon.create(**coupon_params)
        logger.info(f"Created coupon {coupon.id}")
        return coupon
    except Exception as e:
        logger.error(f"Error creating coupon: {str(e)}")
        return None

def refund_charge(charge_id: str, amount: int = None, reason: str = "requested_by_customer"):
    """Create a refund for a charge"""
    logger.info(f"Creating refund for charge: {charge_id}")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        refund_params = {
            "charge": charge_id,
            "reason": reason
        }
        
        if amount is not None:
            refund_params["amount"] = amount
            
        refund = stripe.Refund.create(**refund_params)
        logger.info(f"Created refund {refund.id} for charge {charge_id}")
        return refund
    except Exception as e:
        logger.error(f"Error creating refund: {str(e)}")
        return None

def cancel_subscription_immediately(subscription_id: str):
    """Force cancel a subscription immediately"""
    logger.info(f"Force canceling subscription: {subscription_id}")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        subscription = stripe.Subscription.delete(subscription_id)
        logger.info(f"Cancelled subscription {subscription_id}")
        return subscription
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        return None

def reactivate_subscription(subscription_id: str):
    """Reactivate a canceled subscription"""
    logger.info(f"Reactivating subscription: {subscription_id}")
    
    # Initialize Stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        subscription = stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=False
        )
        logger.info(f"Reactivated subscription {subscription_id}")
        return subscription
    except Exception as e:
        logger.error(f"Error reactivating subscription: {str(e)}")
        return None

def main():
    """Main entry point for the script"""
    parser = argparse.ArgumentParser(description="Stripe admin tools")
    parser.add_argument(
        "command",
        choices=["sync-customers", "sync-subscriptions", "create-coupon", "refund-charge", "cancel-subscription", "reactivate-subscription"],
        help="Command to execute"
    )
    parser.add_argument("--name", help="Coupon name")
    parser.add_argument("--duration", help="Coupon duration (once, forever, repeating)")
    parser.add_argument("--amount-off", type=int, help="Amount off in cents")
    parser.add_argument("--percent-off", type=int, help="Percent off")
    parser.add_argument("--currency", help="Currency for amount off")
    parser.add_argument("--max-redemptions", type=int, help="Maximum redemptions")
    parser.add_argument("--charge-id", help="Charge ID for refund")
    parser.add_argument("--subscription-id", help="Subscription ID")
    parser.add_argument("--reason", help="Refund reason")
    parser.add_argument("--amount", type=int, help="Refund amount in cents")
    
    args = parser.parse_args()
    
    if args.command == "sync-customers":
        sync_customers()
    elif args.command == "sync-subscriptions":
        sync_subscriptions()
    elif args.command == "create-coupon":
        if not args.name or not args.duration:
            logger.error("Coupon name and duration are required")
            return
        
        create_coupon(
            args.name,
            args.duration,
            args.amount_off,
            args.percent_off,
            args.currency,
            args.max_redemptions
        )
    elif args.command == "refund-charge":
        if not args.charge_id:
            logger.error("Charge ID is required")
            return
            
        refund_charge(
            args.charge_id,
            args.amount,
            args.reason or "requested_by_customer"
        )
    elif args.command == "cancel-subscription":
        if not args.subscription_id:
            logger.error("Subscription ID is required")
            return
            
        cancel_subscription_immediately(args.subscription_id)
    elif args.command == "reactivate-subscription":
        if not args.subscription_id:
            logger.error("Subscription ID is required")
            return
            
        reactivate_subscription(args.subscription_id)

if __name__ == "__main__":
    main()