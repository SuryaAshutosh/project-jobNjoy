import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '@/services/api';

const ResetPassword = () => {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  useEffect(() => {
    // Check if token is present
    if (!token) {
      setError('Invalid or missing reset token. Please use the link from your email.');
    }
  }, [token]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    
    if (!token) {
      setError('Invalid or missing reset token');
      return;
    }
    
    if (!password) {
      setError('Password is required');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    setLoading(true);
    
    try {
      // Fix: Send data as form data, not JSON object
      const response = await api.post('/auth/reset-password', new URLSearchParams({ token, new_password: password }), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      setMessage(response.data.message);
      // Redirect to login after a short delay
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to reset password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f9fafb', padding: '1rem' }}>
      <div style={{ width: '100%', maxWidth: '28rem', backgroundColor: 'white', borderRadius: '0.5rem', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)', padding: '1.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: '700' }}>Reset Password</h1>
          <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
            Enter your new password below.
          </p>
        </div>
        
        {error && (
          <div style={{ backgroundColor: '#fee2e2', color: '#b91c1c', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>
            {error}
          </div>
        )}
        
        {message && (
          <div style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '0.75rem', borderRadius: '0.375rem', marginBottom: '1rem' }}>
            {message}
          </div>
        )}
        
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ position: 'relative' }}>
            <label htmlFor="password" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>New Password</label>
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your new password"
              style={{ width: '100%', padding: '0.75rem', borderRadius: '0.375rem', border: '1px solid #d1d5db', fontSize: '0.875rem', paddingRight: '3.5rem' }}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{ 
                position: 'absolute', 
                right: '0.75rem', 
                top: '50%', 
                transform: 'translateY(-50%)', 
                background: 'none', 
                border: 'none', 
                cursor: 'pointer',
                color: '#6b7280',
                fontSize: '0.875rem',
                padding: '0.25rem'
              }}
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>
          
          <div style={{ position: 'relative' }}>
            <label htmlFor="confirmPassword" style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: '500' }}>Confirm Password</label>
            <input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Confirm your new password"
              style={{ width: '100%', padding: '0.75rem', borderRadius: '0.375rem', border: '1px solid #d1d5db', fontSize: '0.875rem', paddingRight: '3.5rem' }}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              style={{ 
                position: 'absolute', 
                right: '0.75rem', 
                top: '50%', 
                transform: 'translateY(-50%)', 
                background: 'none', 
                border: 'none', 
                cursor: 'pointer',
                color: '#6b7280',
                fontSize: '0.875rem',
                padding: '0.25rem'
              }}
            >
              {showConfirmPassword ? 'Hide' : 'Show'}
            </button>
          </div>
          
          <button 
            type="submit" 
            disabled={loading}
            style={{ 
              backgroundColor: loading ? '#9ca3af' : '#2563eb', 
              color: 'white', 
              padding: '0.75rem 1rem', 
              borderRadius: '0.375rem', 
              fontWeight: '500',
              cursor: loading ? 'not-allowed' : 'pointer',
              border: 'none',
              fontSize: '0.875rem'
            }}
          >
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
        
        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: '#6b7280' }}>
          <Link to="/login" style={{ color: '#2563eb', textDecoration: 'underline' }}>
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;