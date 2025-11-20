"""
Unit tests for the Stripe client service
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.stripe_client import StripeClient, STRIPE_PLANS
from app.schemas.schemas import BillingCreate, BillingUpdate
from app.models.db_models import User
import stripe

class TestStripeClient:
    """Test suite for the StripeClient class"""
    
    @pytest.fixture
    def stripe_client(self):
        """Create a StripeClient instance for testing"""
        return StripeClient()
    
    @pytest.fixture
    def mock_user(self):
        """Create a mock user for testing"""
        user = Mock(spec=User)
        user.id = "test-user-id"
        user.email = "test@example.com"
        user.name = "Test User"
        return user
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session for testing"""
        return Mock()
    
    def test_init(self, stripe_client):
        """Test StripeClient initialization"""
        assert stripe_client.stripe == stripe
        assert stripe_client.stripe.api_key is not None
    
    @patch('app.services.stripe_client.stripe.Customer.create')
    @patch('app.services.stripe_client.get_billing_by_user')
    def test_ensure_stripe_customer_creates_new_customer(self, mock_get_billing, mock_customer_create, stripe_client, mock_user, mock_db):
        """Test that ensure_stripe_customer creates a new customer when none exists"""
        # Setup
        mock_get_billing.return_value = None
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        mock_customer_create.return_value = mock_customer
        
        # Execute
        customer_id = stripe_client.ensure_stripe_customer(mock_db, mock_user)
        
        # Assert
        assert customer_id == "cus_test123"
        mock_customer_create.assert_called_once_with(
            email=mock_user.email,
            name=mock_user.name,
            metadata={
                "user_id": str(mock_user.id),
                "created_via": "jobbuddy_platform"
            }
        )
        mock_get_billing.assert_called_once_with(mock_db, mock_user.id)
    
    @patch('app.services.stripe_client.stripe.Customer.create')
    @patch('app.services.stripe_client.get_billing_by_user')
    @patch('app.services.stripe_client.update_billing')
    def test_ensure_stripe_customer_updates_existing_billing(self, mock_update_billing, mock_get_billing, mock_customer_create, stripe_client, mock_user, mock_db):
        """Test that ensure_stripe_customer updates existing billing record"""
        # Setup
        mock_billing = Mock()
        mock_billing.stripe_customer_id = None
        mock_get_billing.return_value = mock_billing
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        mock_customer_create.return_value = mock_customer
        
        # Execute
        customer_id = stripe_client.ensure_stripe_customer(mock_db, mock_user)
        
        # Assert
        assert customer_id == "cus_test123"
        mock_update_billing.assert_called_once()
    
    @patch('app.services.stripe_client.stripe.Customer.create')
    @patch('app.services.stripe_client.get_billing_by_user')
    @patch('app.services.stripe_client.create_billing')
    def test_ensure_stripe_customer_creates_billing_record(self, mock_create_billing, mock_get_billing, mock_customer_create, stripe_client, mock_user, mock_db):
        """Test that ensure_stripe_customer creates a new billing record"""
        # Setup
        mock_get_billing.return_value = None
        mock_customer = Mock()
        mock_customer.id = "cus_test123"
        mock_customer_create.return_value = mock_customer
        
        # Execute
        customer_id = stripe_client.ensure_stripe_customer(mock_db, mock_user)
        
        # Assert
        assert customer_id == "cus_test123"
        mock_create_billing.assert_called_once()
    
    @patch('app.services.stripe_client.stripe.checkout.Session.create')
    def test_create_checkout_session_success(self, mock_session_create, stripe_client, mock_user, mock_db):
        """Test successful creation of checkout session"""
        # Setup
        mock_session = Mock()
        mock_session.id = "cs_test123"
        mock_session.url = "https://checkout.stripe.com/test"
        mock_session.status = "open"
        mock_session_create.return_value = mock_session
        
        # Execute
        result = stripe_client.create_checkout_session(
            mock_db, mock_user, "basic", "https://success.com", "https://cancel.com"
        )
        
        # Assert
        assert result["id"] == "cs_test123"
        assert result["url"] == "https://checkout.stripe.com/test"
        assert result["status"] == "open"
        mock_session_create.assert_called_once()
    
    def test_create_checkout_session_invalid_plan(self, stripe_client, mock_user, mock_db):
        """Test that create_checkout_session raises exception for invalid plan"""
        # Execute & Assert
        with pytest.raises(Exception):
            stripe_client.create_checkout_session(
                mock_db, mock_user, "invalid_plan", "https://success.com", "https://cancel.com"
            )
    
    @patch('app.services.stripe_client.stripe.billing_portal.Session.create')
    def test_create_portal_session_success(self, mock_portal_create, stripe_client, mock_user, mock_db):
        """Test successful creation of portal session"""
        # Setup
        mock_session = Mock()
        mock_session.url = "https://billing.stripe.com/test"
        mock_portal_create.return_value = mock_session
        
        with patch.object(stripe_client, 'ensure_stripe_customer', return_value="cus_test123"):
            # Execute
            result = stripe_client.create_portal_session(mock_db, mock_user)
            
            # Assert
            assert result["url"] == "https://billing.stripe.com/test"
            mock_portal_create.assert_called_once_with(
                customer="cus_test123",
                return_url=None
            )
    
    @patch('app.services.stripe_client.stripe.PaymentIntent.create')
    def test_create_invoice_payment_intent_success(self, mock_payment_intent_create, stripe_client, mock_user, mock_db):
        """Test successful creation of payment intent"""
        # Setup
        mock_payment_intent = Mock()
        mock_payment_intent.id = "pi_test123"
        mock_payment_intent.client_secret = "secret_test123"
        mock_payment_intent.status = "requires_payment_method"
        mock_payment_intent_create.return_value = mock_payment_intent
        
        with patch.object(stripe_client, 'ensure_stripe_customer', return_value="cus_test123"):
            # Execute
            result = stripe_client.create_invoice_payment_intent(
                mock_db, mock_user, 1000, "usd", "Test payment"
            )
            
            # Assert
            assert result["id"] == "pi_test123"
            assert result["client_secret"] == "secret_test123"
            assert result["status"] == "requires_payment_method"
            mock_payment_intent_create.assert_called_once_with(
                amount=1000,
                currency="usd",
                customer="cus_test123",
                description="Test payment",
                automatic_payment_methods={"enabled": True}
            )
    
    @patch('app.services.stripe_client.stripe.Subscription.retrieve')
    @patch('app.services.stripe_client.stripe.Subscription.modify')
    def test_cancel_subscription_at_period_end(self, mock_subscription_modify, mock_subscription_retrieve, stripe_client, mock_user, mock_db):
        """Test canceling subscription at period end"""
        # Setup
        mock_subscription = Mock()
        mock_subscription.id = "sub_test123"
        mock_subscription.cancel_at_period_end = False
        mock_subscription.status = "active"
        mock_subscription.current_period_end = 1234567890
        mock_subscription_retrieve.return_value = mock_subscription
        
        mock_updated_subscription = Mock()
        mock_updated_subscription.id = "sub_test123"
        mock_updated_subscription.cancel_at_period_end = True
        mock_updated_subscription.status = "active"
        mock_subscription_modify.return_value = mock_updated_subscription
        
        mock_billing = Mock()
        mock_billing.stripe_subscription_id = "sub_test123"
        with patch('app.services.stripe_client.get_billing_by_user', return_value=mock_billing):
            with patch('app.services.stripe_client.update_billing') as mock_update_billing:
                # Execute
                result = stripe_client.cancel_subscription(mock_db, mock_user, at_period_end=True)
                
                # Assert
                assert result["status"] == "scheduled_for_cancellation"
                assert result["subscription_id"] == "sub_test123"
                assert result["cancel_at_period_end"] is True
                mock_subscription_modify.assert_called_once_with(
                    "sub_test123",
                    cancel_at_period_end=True
                )
    
    @patch('app.services.stripe_client.stripe.Subscription.retrieve')
    @patch('app.services.stripe_client.stripe.Subscription.delete')
    def test_cancel_subscription_immediately(self, mock_subscription_delete, mock_subscription_retrieve, stripe_client, mock_user, mock_db):
        """Test canceling subscription immediately"""
        # Setup
        mock_subscription = Mock()
        mock_subscription.id = "sub_test123"
        mock_subscription.cancel_at_period_end = False
        mock_subscription.status = "active"
        mock_subscription_retrieve.return_value = mock_subscription
        
        mock_canceled_subscription = Mock()
        mock_canceled_subscription.id = "sub_test123"
        mock_subscription_delete.return_value = mock_canceled_subscription
        
        mock_billing = Mock()
        mock_billing.stripe_subscription_id = "sub_test123"
        with patch('app.services.stripe_client.get_billing_by_user', return_value=mock_billing):
            with patch('app.services.stripe_client.update_billing') as mock_update_billing:
                # Execute
                result = stripe_client.cancel_subscription(mock_db, mock_user, at_period_end=False)
                
                # Assert
                assert result["status"] == "canceled"
                assert result["subscription_id"] == "sub_test123"
                mock_subscription_delete.assert_called_once_with("sub_test123")
    
    @patch('app.services.stripe_client.stripe.Webhook.construct_event')
    def test_verify_webhook_signature_success(self, mock_construct_event, stripe_client):
        """Test successful webhook signature verification"""
        # Setup
        mock_event = Mock()
        mock_construct_event.return_value = mock_event
        
        # Execute
        result = stripe_client.verify_webhook_signature(b"payload", "signature", "secret")
        
        # Assert
        assert result == mock_event
        mock_construct_event.assert_called_once_with(b"payload", "signature", "secret")
    
    @patch('app.services.stripe_client.stripe.Webhook.construct_event')
    def test_verify_webhook_signature_invalid_payload(self, mock_construct_event, stripe_client):
        """Test webhook signature verification with invalid payload"""
        # Setup
        mock_construct_event.side_effect = ValueError("Invalid payload")
        
        # Execute
        result = stripe_client.verify_webhook_signature(b"payload", "signature", "secret")
        
        # Assert
        assert result is None
    
    @patch('app.services.stripe_client.stripe.Webhook.construct_event')
    def test_verify_webhook_signature_invalid_signature(self, mock_construct_event, stripe_client):
        """Test webhook signature verification with invalid signature"""
        # Setup
        mock_construct_event.side_effect = stripe.error.SignatureVerificationError("Invalid signature", "header")
        
        # Execute
        result = stripe_client.verify_webhook_signature(b"payload", "signature", "secret")
        
        # Assert
        assert result is None