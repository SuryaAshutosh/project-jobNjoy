# Stripe Integration for JobBuddy

This document provides comprehensive documentation for the Stripe integration in the JobBuddy platform.

## Overview

The Stripe integration enables subscription-based billing with plans (Free, Basic, Pro, Unlimited), one-time purchases, trial periods, and promo coupon handling. It ensures backend updates user.subscription_status based on Stripe events and exposes secure endpoints for creating checkout sessions and managing subscriptions.

## Features Implemented

1. **Subscription-based billing** with plans: Free (limited), Basic, Pro, Unlimited
2. **One-time purchases** (optional add-ons like resume review)
3. **Trial periods** and promo coupon handling
4. **Webhook handling** for real-time updates
5. **Customer Portal integration** for self-service billing management
6. **Idempotency handling** to ensure each Stripe event is processed once
7. **Retry/backoff mechanisms** for transient errors
8. **Admin tools** for Stripe management
9. **Comprehensive testing** with unit and integration tests

## Backend Implementation

### File Structure

```
backend/
├── app/
│   ├── api/routers/payments.py          # Payment endpoints
│   ├── services/stripe_client.py        # Stripe client service
│   ├── crud/crud_billing.py             # Billing CRUD operations
│   └── models/db_models.py              # Billing database model
├── scripts/
│   ├── sync_stripe.py                   # Admin tools for Stripe management
│   ├── billing_migration.sql            # Database migration script
│   └── alembic_billing_migration.py     # Alembic migration file
├── tests/
│   ├── test_stripe_client.py            # Unit tests for Stripe client
│   └── test_payments_webhook.py         # Unit tests for webhook endpoint
└── .env.example                         # Environment variables
```

### Endpoints

1. `POST /payments/create-checkout-session`
   - Creates Stripe Customer (if not exists), Checkout Session, returns session.url or session.id
   - Body: `{ plan_id, success_url, cancel_url, trial_days?, coupon? }`

2. `POST /payments/create-portal-session`
   - Creates Stripe Customer Portal session for self-service billing management

3. `POST /payments/create-invoice-payment-intent`
   - Creates PaymentIntent for one-time purchases

4. `POST /payments/webhook`
   - Secure endpoint to receive Stripe events and update DB
   - Supports: checkout.session.completed, invoice.paid, invoice.payment_failed, customer.subscription.updated, customer.subscription.deleted, charge.refunded

5. `GET /payments/status`
   - Returns current subscription status for logged-in user

6. `POST /payments/cancel-subscription`
   - Cancel subscription immediately or at period end

7. `POST /payments/reactivate-subscription`
   - Reactivate a canceled subscription

8. `GET /payments/invoices`
   - List invoices for the user

9. `GET /payments/billing`
   - Get billing information for the current user

### Database Schema

The [Billing](file:///C:/Users/Surya/Desktop/New%20folder/jobNjoy-project/backend/app/models/db_models.py#L133-L149) table includes the following fields:

- `id` (UUID)
- `user_id` (FK)
- `stripe_customer_id`
- `stripe_subscription_id`
- `plan`
- `status`
- `current_period_start`
- `current_period_end`
- `cancel_at_period_end` (bool)
- `metadata` (JSONB)
- `created_at`
- `updated_at`

### Security Features

1. **Stripe signature verification** with `STRIPE_WEBHOOK_SECRET`
2. **Idempotency guard** using `stripe_event_id` storage
3. **Retry/backoff** for transient errors when calling Stripe
4. **Secure patterns** - server-created Checkout Sessions and Customer Portal sessions
5. **No sensitive data** logged (masked webhook payloads)

## Frontend Implementation

### File Structure

```
frontend/
├── src/
│   ├── pages/Billing.jsx                # Billing page with plan selection and invoice history
│   ├── hooks/useBilling.js              # React hook for billing operations
```

### Features

1. **Billing page** showing current plan, next billing date, cancel/reactivate buttons
2. **Checkout flow** calling POST /payments/create-checkout-session and redirecting to Stripe Checkout
3. **Manage billing button** opening Stripe Customer Portal session
4. **Invoices list** with download links
5. **Trial expiry banner** and friendly UI messages

## Environment Variables

The following environment variables need to be set in `.env`:

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_PRICE_BASIC=price_basic_placeholder
STRIPE_PRICE_PRO=price_pro_placeholder
STRIPE_PRICE_UNLIMITED=price_unlimited_placeholder
STRIPE_TRIAL_DAYS_BASIC=7
STRIPE_TRIAL_DAYS_PRO=14
STRIPE_TRIAL_DAYS_UNLIMITED=14
STRIPE_PORTAL_RETURN_URL=http://localhost:3000/billing
STRIPE_API_VERSION=2023-10-16
STRIPE_TAX_ENABLED=false
```

## Setup Instructions

### 1. Stripe Account Setup

1. Create a Stripe account at https://stripe.com
2. Get your API keys from the Stripe Dashboard
3. Create products and prices for each plan in the Stripe Dashboard:
   - Basic Plan
   - Pro Plan
   - Unlimited Plan
4. Set up webhooks in the Stripe Dashboard:
   - Endpoint URL: `https://yourdomain.com/api/payments/webhook`
   - Events to listen for:
     - `checkout.session.completed`
     - `invoice.paid`
     - `invoice.payment_failed`
     - `customer.subscription.updated`
     - `customer.subscription.deleted`
     - `charge.refunded`

### 2. Database Migration

Run the SQL migration script to update your database schema:

```bash
psql -d your_database_name -f backend/scripts/billing_migration.sql
```

### 3. Environment Configuration

Update your `.env` file with the Stripe credentials and price IDs:

```bash
# Stripe
STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_PRICE_BASIC=price_XXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_PRICE_PRO=price_XXXXXXXXXXXXXXXXXXXXXXXX
STRIPE_PRICE_UNLIMITED=price_XXXXXXXXXXXXXXXXXXXXXXXX
```

## Testing

### Unit Tests

Run the unit tests for the Stripe integration:

```bash
cd backend
pytest tests/test_stripe_client.py -v
pytest tests/test_payments_webhook.py -v
```

### Local Testing with Stripe CLI

1. Install the Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhooks to your local server:

```bash
stripe listen --forward-to localhost:8000/api/payments/webhook
```

3. Test webhook events:

```bash
stripe trigger checkout.session.completed
stripe trigger invoice.paid
stripe trigger customer.subscription.updated
```

### Test Cards

Use these test card numbers for development:

- Successful payment: `4242 4242 4242 4242`
- Insufficient funds: `4000 0000 0000 0002`
- Expired card: `4000 0000 0000 0069`
- Authentication required: `4000 0025 0000 3155`

## Admin Tools

The `scripts/sync_stripe.py` script provides admin tools for Stripe management:

```bash
# Sync all Stripe customers with local database
python backend/scripts/sync_stripe.py sync-customers

# Sync all Stripe subscriptions with local database
python backend/scripts/sync_stripe.py sync-subscriptions

# Create a promotional coupon
python backend/scripts/sync_stripe.py create-coupon --name "TEST20" --duration "once" --percent-off 20

# Refund a charge
python backend/scripts/sync_stripe.py refund-charge --charge-id ch_XXXXXXXXXXXXXXXXXXXXXXXX

# Force cancel a subscription
python backend/scripts/sync_stripe.py cancel-subscription --subscription-id sub_XXXXXXXXXXXXXXXXXXXXXXXX

# Reactivate a canceled subscription
python backend/scripts/sync_stripe.py reactivate-subscription --subscription-id sub_XXXXXXXXXXXXXXXXXXXXXXXX
```

## Compliance & Security

1. **PCI Compliance**: Uses Stripe-hosted pages (Checkout & Customer Portal)
2. **Data Privacy**: Does not persist full card numbers or CVC anywhere
3. **HTTPS**: All webhook and checkout endpoints use HTTPS
4. **GDPR**: Supports user requests for invoices and deletion of billing data
5. **Logging**: No PII in logs, masked webhook payloads

## Monitoring & Alerts

Key metrics to monitor:

- `subscriptions_created_total`
- `subscription_cancellations_total`
- `webhook_events_processed_total`
- `payment_failures_total`

Set up alerts for:

- Failed webhooks
- Failed invoice payments
- High error rates in payment processing

## Error Handling

The integration handles various error scenarios:

- Card declines
- Incomplete payments
- Disputed charges
- Expired cards
- Chargebacks

For payment failures, users are marked as in grace period (configurable days) before restricting access.

## Checklist of Created Files

- [x] `backend/app/models/db_models.py` - Enhanced Billing model
- [x] `backend/app/schemas/schemas.py` - Updated billing schemas
- [x] `backend/app/services/stripe_client.py` - Stripe client service
- [x] `backend/app/api/routers/payments.py` - Payment endpoints
- [x] `backend/app/crud/crud_billing.py` - Billing CRUD operations
- [x] `backend/scripts/billing_migration.sql` - Database migration script
- [x] `backend/scripts/alembic_billing_migration.py` - Alembic migration file
- [x] `backend/scripts/sync_stripe.py` - Admin tools
- [x] `backend/tests/test_stripe_client.py` - Unit tests
- [x] `backend/tests/test_payments_webhook.py` - Webhook tests
- [x] `frontend/src/pages/Billing.jsx` - Billing page
- [x] `frontend/src/hooks/useBilling.js` - Billing hook
- [x] `backend/.env.example` - Environment variables

## Quick Runbook for Local Testing

1. **Start the backend server**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

2. **Start the Stripe webhook listener**:
   ```bash
   stripe listen --forward-to localhost:8000/api/payments/webhook
   ```

3. **Set up environment variables** in `.env`:
   ```bash
   STRIPE_SECRET_KEY=sk_test_XXXXXXXXXXXXXXXXXXXXXXXX
   STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   STRIPE_PRICE_BASIC=price_XXXXXXXXXXXXXXXXXXXXXXXX
   STRIPE_PRICE_PRO=price_XXXXXXXXXXXXXXXXXXXXXXXX
   STRIPE_PRICE_UNLIMITED=price_XXXXXXXXXXXXXXXXXXXXXXXX
   ```

4. **Run database migration**:
   ```bash
   psql -d your_database_name -f backend/scripts/billing_migration.sql
   ```

5. **Test the integration**:
   - Create a checkout session using the API
   - Complete checkout with test card `4242 4242 4242 4242`
   - Confirm webhook is processed
   - Confirm user.subscription_status is updated

## Deployment Checklist

1. [ ] Set up Stripe account and obtain API keys
2. [ ] Create products and prices in Stripe Dashboard
3. [ ] Configure webhooks in Stripe Dashboard
4. [ ] Update production environment variables
5. [ ] Run database migration
6. [ ] Deploy backend and frontend
7. [ ] Test end-to-end flow
8. [ ] Set up monitoring and alerts
9. [ ] Configure email notifications for invoices
10. [ ] Set up dunning settings in Stripe Dashboard

## Assumptions Made

1. Stripe account has created product and price IDs
2. Database is PostgreSQL with JSONB support
3. Application uses FastAPI for backend and React for frontend
4. Environment variables are properly configured
5. SSL certificates are used in production
6. Proper error handling and logging are implemented
7. Idempotency is handled for webhook processing
8. Retry mechanisms are in place for transient errors

## Next Steps

1. Perform end-to-end testing using stripe-cli
2. Add billing emails for invoice notifications
3. Set up email receipts and dunning settings in Stripe Dashboard
4. Configure monitoring and alerting for payment failures
5. Implement additional security measures as needed
6. Add more comprehensive test coverage
7. Document any custom business logic specific to your use case