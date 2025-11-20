# Stripe API Curl Examples

This document provides example curl commands for testing the Stripe integration endpoints.

## Prerequisites

1. Start the backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. Obtain a valid JWT token by logging in through the application

3. Set the token as an environment variable:
   ```bash
   export TOKEN=your_jwt_token_here
   ```

## Payment Endpoints

### Create Checkout Session

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_id": "pro",
    "success_url": "https://app.example.com/billing/success",
    "cancel_url": "https://app.example.com/billing/cancel",
    "trial_days": 14
  }' \
  http://localhost:8000/api/payments/create-checkout-session
```

### Create Portal Session

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/payments/create-portal-session
```

### Create Invoice Payment Intent

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1999,
    "currency": "usd",
    "description": "One-time resume review service"
  }' \
  http://localhost:8000/api/payments/create-invoice-payment-intent
```

### Get Payment Status

```bash
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/payments/status
```

### Cancel Subscription

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "at_period_end": true
  }' \
  http://localhost:8000/api/payments/cancel-subscription
```

### Reactivate Subscription

```bash
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  http://localhost:8000/api/payments/reactivate-subscription
```

### List Invoices

```bash
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/payments/invoices
```

### Get Billing Information

```bash
curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/payments/billing
```

## Webhook Testing

### Using Stripe CLI

1. Start the webhook listener:
   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook
   ```

2. Trigger test events:
   ```bash
   # Trigger a successful checkout session
   stripe trigger checkout.session.completed
   
   # Trigger a paid invoice
   stripe trigger invoice.paid
   
   # Trigger a failed payment
   stripe trigger invoice.payment_failed
   
   # Trigger a subscription update
   stripe trigger customer.subscription.updated
   
   # Trigger a subscription cancellation
   stripe trigger customer.subscription.deleted
   
   # Trigger a refund
   stripe trigger charge.refunded
   ```

## Admin Commands

### Sync Stripe Data

```bash
# Sync customers
python backend/scripts/sync_stripe.py sync-customers

# Sync subscriptions
python backend/scripts/sync_stripe.py sync-subscriptions
```

### Create Coupon

```bash
# Create a 20% off coupon
python backend/scripts/sync_stripe.py create-coupon \
  --name "SAVE20" \
  --duration "once" \
  --percent-off 20

# Create a $10 off coupon
python backend/scripts/sync_stripe.py create-coupon \
  --name "SAVE10" \
  --duration "once" \
  --amount-off 1000 \
  --currency "usd"
```

### Refund a Charge

```bash
python backend/scripts/sync_stripe.py refund-charge \
  --charge-id ch_XXXXXXXXXXXXXXXXXXXXXXXX \
  --amount 999 \
  --reason "customer_request"
```

### Manage Subscriptions

```bash
# Cancel a subscription immediately
python backend/scripts/sync_stripe.py cancel-subscription \
  --subscription-id sub_XXXXXXXXXXXXXXXXXXXXXXXX

# Reactivate a canceled subscription
python backend/scripts/sync_stripe.py reactivate-subscription \
  --subscription-id sub_XXXXXXXXXXXXXXXXXXXXXXXX
```

## Test Card Numbers

Use these test card numbers for development:

- **Successful payment**: `4242 4242 4242 4242`
- **Insufficient funds**: `4000 0000 0000 0002`
- **Expired card**: `4000 0000 0000 0069`
- **Authentication required**: `4000 0025 0000 3155`
- **Visa debit**: `4000 0000 0000 0019`
- **Mastercard**: `5555 5555 5555 4444`
- **American Express**: `3782 822463 10005`

## Webhook Verification Example

Here's a sample webhook verification code snippet showing how to verify signature using `stripe.Webhook.construct_event`:

```python
import stripe
from fastapi import HTTPException, status

def verify_webhook_signature(payload: bytes, sig_header: str, webhook_secret: str):
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
        return None
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return None

# Usage in webhook endpoint
# payload = await request.body()
# event = verify_webhook_signature(payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET)
# if not event:
#     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook signature")
```

This example demonstrates the core webhook verification logic used in the implementation.