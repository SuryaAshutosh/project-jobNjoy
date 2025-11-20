import React, { useState, useEffect } from 'react';
import api from '../services/api';

const BillingPage = () => {
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [plans, setPlans] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [isCanceling, setIsCanceling] = useState(false);
  const [isReactivating, setIsReactivating] = useState(false);
  const [showPlans, setShowPlans] = useState(false);

  // Fetch billing information
  useEffect(() => {
    const fetchBilling = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await api.get('/payments/billing');
        setBilling(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch billing information');
      } finally {
        setLoading(false);
      }
    };

    fetchBilling();
  }, []);

  // Fetch invoices
  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const response = await api.get('/payments/invoices');
        setInvoices(response.data);
      } catch (err) {
        console.error('Failed to fetch invoices:', err);
      }
    };

    if (billing) {
      fetchInvoices();
    }
  }, [billing]);

  const handleCheckout = async (planId) => {
    try {
      const response = await api.post('/payments/create-checkout-session', {
        plan_id: planId,
        success_url: `${window.location.origin}/billing?success=true`,
        cancel_url: `${window.location.origin}/billing?canceled=true`
      });

      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (err) {
      console.error('Failed to create checkout session:', err);
      alert('Failed to start checkout process. Please try again.');
    }
  };

  const handleManageBilling = async () => {
    try {
      const response = await api.post('/payments/create-portal-session');
      if (response.data.url) {
        window.location.href = response.data.url;
      }
    } catch (err) {
      console.error('Failed to create portal session:', err);
      alert('Failed to open billing portal. Please try again.');
    }
  };

  const handleCancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    setIsCanceling(true);
    try {
      await api.post('/payments/cancel-subscription', {
        at_period_end: true
      });
      
      // Refresh billing info
      const response = await api.get('/payments/billing');
      setBilling(response.data);
      
      alert('Subscription canceled successfully. You will retain access until the end of your billing period.');
    } catch (err) {
      console.error('Failed to cancel subscription:', err);
      alert('Failed to cancel subscription. Please try again.');
    } finally {
      setIsCanceling(false);
    }
  };

  const handleReactivateSubscription = async () => {
    setIsReactivating(true);
    try {
      await api.post('/payments/reactivate-subscription');
      
      // Refresh billing info
      const response = await api.get('/payments/billing');
      setBilling(response.data);
      
      alert('Subscription reactivated successfully!');
    } catch (err) {
      console.error('Failed to reactivate subscription:', err);
      alert('Failed to reactivate subscription. Please try again.');
    } finally {
      setIsReactivating(false);
    }
  };

  const formatCurrency = (amount, currency = 'usd') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
    }).format(amount / 100);
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '64' }}>
        <div style={{ 
          animation: 'spin 1s linear infinite',
          borderRadius: '9999px',
          height: '3rem',
          width: '3rem',
          borderTopWidth: '2px',
          borderColor: '#2563eb'
        }}></div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        backgroundColor: '#fef2f2', 
        border: '1px solid #fecaca', 
        borderRadius: '0.5rem', 
        padding: '1rem' 
      }}>
        <h2 style={{ color: '#991b1b', fontSize: '1.125rem', fontWeight: '500' }}>Error</h2>
        <p style={{ color: '#b91c1c' }}>{error}</p>
        <button 
          onClick={() => window.location.reload()} 
          style={{ 
            marginTop: '1rem',
            backgroundColor: '#2563eb',
            color: 'white',
            padding: '0.5rem 1rem',
            borderRadius: '0.375rem',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  const currentPlan = billing?.plan || 'free';
  const isSubscribed = currentPlan !== 'free' && billing?.status === 'active';
  const isCanceled = billing?.cancel_at_period_end;

  return (
    <div style={{ maxWidth: '6xl', margin: '0 auto', padding: '1rem' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '1.875rem', fontWeight: '700', color: '#111827' }}>Billing & Subscription</h1>
        <p style={{ color: '#6b7280', marginTop: '0.5rem' }}>Manage your subscription and payment information</p>
      </div>

      {/* Current Plan Card */}
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '0.5rem', 
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', 
        padding: '1.5rem', 
        marginBottom: '2rem' 
      }}>
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          gap: '1rem'
        }}>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: '#111827' }}>Current Plan</h2>
            <div style={{ marginTop: '0.5rem' }}>
              <span style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', textTransform: 'capitalize' }}>
                {currentPlan}
              </span>
              {isSubscribed && (
                <span style={{ 
                  marginLeft: '0.5rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '0.125rem 0.625rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  backgroundColor: '#dcfce7',
                  color: '#166534'
                }}>
                  Active
                </span>
              )}
              {isCanceled && (
                <span style={{ 
                  marginLeft: '0.5rem',
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '0.125rem 0.625rem',
                  borderRadius: '9999px',
                  fontSize: '0.75rem',
                  fontWeight: '500',
                  backgroundColor: '#fef9c3',
                  color: '#854d0e'
                }}>
                  Canceled
                </span>
              )}
            </div>
            {billing?.current_period_end && (
              <p style={{ color: '#6b7280', marginTop: '0.25rem' }}>
                {isCanceled 
                  ? `Expires on ${formatDate(billing.current_period_end)}` 
                  : `Renews on ${formatDate(billing.current_period_end)}`}
              </p>
            )}
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button 
              onClick={handleManageBilling}
              style={{
                backgroundColor: '#f3f4f6',
                color: '#1f2937',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: 'none',
                cursor: 'pointer',
                fontWeight: '500'
              }}
            >
              Manage Billing
            </button>
            {isSubscribed && !isCanceled && (
              <button 
                onClick={handleCancelSubscription}
                disabled={isCanceling}
                style={{
                  backgroundColor: '#fee2e2',
                  color: '#991b1b',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.375rem',
                  border: 'none',
                  cursor: isCanceling ? 'not-allowed' : 'pointer',
                  fontWeight: '500',
                  opacity: isCanceling ? 0.7 : 1
                }}
              >
                {isCanceling ? 'Canceling...' : 'Cancel Subscription'}
              </button>
            )}
            {isCanceled && (
              <button 
                onClick={handleReactivateSubscription}
                disabled={isReactivating}
                style={{
                  backgroundColor: '#dcfce7',
                  color: '#166534',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.375rem',
                  border: 'none',
                  cursor: isReactivating ? 'not-allowed' : 'pointer',
                  fontWeight: '500',
                  opacity: isReactivating ? 0.7 : 1
                }}
              >
                {isReactivating ? 'Reactivating...' : 'Reactivate Subscription'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Plan Selection */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center', 
          marginBottom: '1.5rem' 
        }}>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827' }}>Choose a Plan</h2>
          <button 
            onClick={() => setShowPlans(!showPlans)}
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: 'none',
              cursor: 'pointer',
              fontWeight: '500'
            }}
          >
            {showPlans ? 'Hide Plans' : 'View Plans'}
          </button>
        </div>

        {showPlans && (
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
            gap: '1.5rem' 
          }}>
            {[
              {
                id: 'basic',
                name: 'Basic',
                price: '$9.99/month',
                features: ['Up to 10 job applications/month', 'Basic resume parsing', 'Email support']
              },
              {
                id: 'pro',
                name: 'Pro',
                price: '$29.99/month',
                features: ['Unlimited job applications', 'Advanced resume parsing', 'Priority support', 'AI job matching'],
                popular: true
              },
              {
                id: 'unlimited',
                name: 'Unlimited',
                price: '$49.99/month',
                features: ['Unlimited job applications', 'Advanced resume parsing', '24/7 priority support', 'AI job matching', 'Personalized coaching']
              }
            ].map((plan) => (
              <div 
                key={plan.id} 
                style={{
                  border: `1px solid ${plan.popular ? '#3b82f6' : '#e5e7eb'}`,
                  borderRadius: '0.5rem',
                  padding: '1.5rem',
                  position: 'relative',
                  boxShadow: plan.popular ? '0 4px 6px -1px rgba(59, 130, 246, 0.2)' : 'none'
                }}
              >
                {plan.popular && (
                  <div style={{
                    position: 'absolute',
                    top: 0,
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    backgroundColor: '#3b82f6',
                    color: 'white',
                    fontSize: '0.75rem',
                    fontWeight: '700',
                    padding: '0.25rem 0.75rem',
                    borderRadius: '9999px'
                  }}>
                    MOST POPULAR
                  </div>
                )}
                <div style={{ marginBottom: '1rem' }}>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#111827' }}>{plan.name}</h3>
                  <p style={{ fontSize: '1.875rem', fontWeight: '700', color: '#111827', marginTop: '0.5rem' }}>{plan.price}</p>
                </div>
                <ul style={{ marginBottom: '1.5rem', paddingLeft: '1.5rem' }}>
                  {plan.features.map((feature, index) => (
                    <li key={index} style={{ marginBottom: '0.75rem', display: 'flex', alignItems: 'flex-start' }}>
                      <svg 
                        style={{ height: '1.25rem', width: '1.25rem', color: '#10b981', marginRight: '0.5rem', marginTop: '0.125rem' }} 
                        fill="none" 
                        viewBox="0 0 24 24" 
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span style={{ color: '#6b7280' }}>{feature}</span>
                    </li>
                  ))}
                </ul>
                <button
                  onClick={() => handleCheckout(plan.id)}
                  style={{
                    width: '100%',
                    backgroundColor: plan.popular ? '#2563eb' : '#f3f4f6',
                    color: plan.popular ? 'white' : '#1f2937',
                    padding: '0.75rem 1rem',
                    borderRadius: '0.375rem',
                    border: 'none',
                    cursor: 'pointer',
                    fontWeight: '500'
                  }}
                  disabled={currentPlan === plan.id && isSubscribed}
                >
                  {currentPlan === plan.id && isSubscribed ? 'Current Plan' : 'Get Started'}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Invoices */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: '700', color: '#111827', marginBottom: '1.5rem' }}>Payment History</h2>
        {invoices.length === 0 ? (
          <div style={{ 
            backgroundColor: '#f9fafb', 
            borderRadius: '0.5rem', 
            padding: '2rem', 
            textAlign: 'center' 
          }}>
            <svg 
              style={{ height: '3rem', width: '3rem', color: '#9ca3af', margin: '0 auto' }} 
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 style={{ marginTop: '0.5rem', fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>No invoices</h3>
            <p style={{ marginTop: '0.25rem', fontSize: '0.875rem', color: '#6b7280' }}>You don't have any invoices yet.</p>
          </div>
        ) : (
          <div style={{ 
            backgroundColor: 'white', 
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', 
            borderRadius: '0.375rem', 
            overflow: 'hidden' 
          }}>
            <ul style={{ divideY: '1px solid #e5e7eb' }}>
              {invoices.map((invoice) => (
                <li key={invoice.id} style={{ padding: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <div style={{ flexShrink: 0 }}>
                      <span style={{
                        padding: '0.125rem 0.5rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        backgroundColor: invoice.status === 'paid' 
                          ? '#dcfce7' 
                          : invoice.status === 'open' 
                            ? '#fef9c3' 
                            : '#fee2e2',
                        color: invoice.status === 'paid' 
                          ? '#166534' 
                          : invoice.status === 'open' 
                            ? '#854d0e' 
                            : '#991b1b'
                      }}>
                        {invoice.status}
                      </span>
                    </div>
                    <div style={{ marginLeft: '1rem' }}>
                      <div style={{ fontSize: '0.875rem', fontWeight: '500', color: '#111827' }}>
                        {formatCurrency(invoice.amount_due, invoice.currency)}
                      </div>
                      <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                        {formatDate(invoice.created)}
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    {invoice.invoice_pdf && (
                      <a 
                        href={invoice.invoice_pdf} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ fontSize: '0.875rem', fontWeight: '500', color: '#2563eb' }}
                      >
                        Download PDF
                      </a>
                    )}
                    {invoice.hosted_invoice_url && (
                      <a 
                        href={invoice.hosted_invoice_url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        style={{ fontSize: '0.875rem', fontWeight: '500', color: '#2563eb' }}
                      >
                        View Invoice
                      </a>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default BillingPage;