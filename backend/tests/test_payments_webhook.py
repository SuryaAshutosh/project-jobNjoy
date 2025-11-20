"""
Unit tests for the payments webhook endpoint
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from fastapi import HTTPException
from app.services.stripe_client import StripeClient
from app.api.routers.payments import stripe_webhook
import stripe

class TestPaymentsWebhook:
    """Test suite for the payments webhook endpoint"""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object"""
        request = Mock()
        request.body = Mock(return_value=b'{"test": "data"}')
        return request
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_valid_signature(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook with valid signature"""
        # Setup
        mock_event = Mock()
        mock_event.type = "checkout.session.completed"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        mock_stripe_client.handle_checkout_session_completed.return_value = {
            "status": "processed",
            "subscription_id": "sub_test123"
        }
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        assert result["processed_event"]["status"] == "processed"
        mock_stripe_client.verify_webhook_signature.assert_called_once()
        mock_stripe_client.handle_checkout_session_completed.assert_called_once()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_invalid_signature(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook with invalid signature"""
        # Setup
        mock_stripe_client.verify_webhook_signature.return_value = None
        
        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            stripe_webhook(mock_request, "invalid_signature", mock_db)
        
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Invalid webhook signature"
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_invoice_paid(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling invoice.paid event"""
        # Setup
        mock_event = Mock()
        mock_event.type = "invoice.paid"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        mock_stripe_client.handle_invoice_paid.return_value = {
            "status": "processed",
            "invoice_id": "in_test123"
        }
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        mock_stripe_client.handle_invoice_paid.assert_called_once()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_invoice_payment_failed(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling invoice.payment_failed event"""
        # Setup
        mock_event = Mock()
        mock_event.type = "invoice.payment_failed"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        mock_stripe_client.handle_invoice_payment_failed.return_value = {
            "status": "processed",
            "invoice_id": "in_test123"
        }
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        mock_stripe_client.handle_invoice_payment_failed.assert_called_once()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_subscription_updated(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling customer.subscription.updated event"""
        # Setup
        mock_event = Mock()
        mock_event.type = "customer.subscription.updated"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        mock_stripe_client.handle_subscription_updated.return_value = {
            "status": "processed",
            "subscription_id": "sub_test123"
        }
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        mock_stripe_client.handle_subscription_updated.assert_called_once()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_subscription_deleted(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling customer.subscription.deleted event"""
        # Setup
        mock_event = Mock()
        mock_event.type = "customer.subscription.deleted"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        mock_stripe_client.handle_subscription_deleted.return_value = {
            "status": "processed",
            "subscription_id": "sub_test123"
        }
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        mock_stripe_client.handle_subscription_deleted.assert_called_once()
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_charge_refunded(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling charge.refunded event"""
        # Setup
        mock_event = Mock()
        mock_event.type = "charge.refunded"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        assert result["processed_event"]["event_type"] == "charge.refunded"
    
    @patch('app.api.routers.payments.stripe_client')
    def test_stripe_webhook_unhandled_event(self, mock_stripe_client, mock_request, mock_db):
        """Test webhook handling unhandled event type"""
        # Setup
        mock_event = Mock()
        mock_event.type = "customer.updated"
        mock_event.id = "evt_test123"
        mock_event.data.object = Mock()
        
        mock_stripe_client.verify_webhook_signature.return_value = mock_event
        
        # Execute
        result = stripe_webhook(mock_request, "valid_signature", mock_db)
        
        # Assert
        assert result["status"] == "success"
        assert result["processed_event"]["status"] == "ignored"
        assert result["processed_event"]["event_type"] == "customer.updated"