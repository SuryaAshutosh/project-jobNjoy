"""
Example of how to verify Stripe webhook signatures
"""

import stripe
import hashlib
import hmac
import json

def verify_stripe_webhook_signature(payload, signature, webhook_secret):
    """
    Verify the signature of a Stripe webhook
    
    Args:
        payload: The webhook payload (bytes)
        signature: The signature from the Stripe-Signature header
        webhook_secret: Your Stripe webhook secret
        
    Returns:
        stripe.Event: The verified event, or None if verification fails
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, signature, webhook_secret
        )
        return event
    except ValueError:
        # Invalid payload
        return None
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return None

# Example usage
if __name__ == "__main__":
    # These would come from the actual webhook request
    payload = b'{"id": "evt_test_webhook", "object": "event"}'
    signature = "t=1492774577,v1=5257a869e7ecebeda32affa62cdca3fa51cad7e77a0e56ff536d0ce8e108d8bd"
    webhook_secret = "whsec_test_secret"
    
    event = verify_stripe_webhook_signature(payload, signature, webhook_secret)
    
    if event:
        print(f"Verified event: {event.id}")
    else:
        print("Failed to verify webhook signature")