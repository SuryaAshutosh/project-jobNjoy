-- Migration script to update billing table with additional fields for Stripe integration
-- This script should be run on your database to add the new columns

-- Add new columns to billing table
ALTER TABLE billing 
ADD COLUMN IF NOT EXISTS current_period_start TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS cancel_at_period_end BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS metadata JSONB,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Update existing records to have updated_at timestamp
UPDATE billing SET updated_at = NOW() WHERE updated_at IS NULL;

-- Create index on stripe_customer_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_billing_stripe_customer_id ON billing (stripe_customer_id);

-- Create index on stripe_subscription_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_billing_stripe_subscription_id ON billing (stripe_subscription_id);