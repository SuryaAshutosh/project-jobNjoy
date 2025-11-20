import React, { useState } from 'react';

const Settings = () => {
  const [name, setName] = useState('John Doe');
  const [email, setEmail] = useState('john.doe@example.com');
  const [notifications, setNotifications] = useState({
    email: true,
    sms: false,
    push: true
  });
  
  const handleNotificationChange = (type) => {
    setNotifications(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, this would save the settings
    alert('Settings saved!');
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem' }}>Settings</h1>
        <p style={{ color: '#6b7280' }}>
          Manage your account settings and preferences
        </p>
      </div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '1fr', 
        gap: '1.5rem',
        maxWidth: '600px'
      }}>
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Profile Information
          </h2>
          
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label 
                htmlFor="name" 
                style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  fontSize: '0.875rem', 
                  fontWeight: '500' 
                }}
              >
                Full Name
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '0.5rem', 
                  borderRadius: '0.375rem', 
                  border: '1px solid #d1d5db', 
                  fontSize: '0.875rem' 
                }}
              />
            </div>
            
            <div style={{ marginBottom: '1.5rem' }}>
              <label 
                htmlFor="email" 
                style={{ 
                  display: 'block', 
                  marginBottom: '0.5rem', 
                  fontSize: '0.875rem', 
                  fontWeight: '500' 
                }}
              >
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                style={{ 
                  width: '100%', 
                  padding: '0.5rem', 
                  borderRadius: '0.375rem', 
                  border: '1px solid #d1d5db', 
                  fontSize: '0.875rem' 
                }}
              />
            </div>
            
            <button
              type="submit"
              style={{
                backgroundColor: '#2563eb',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: 'none',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Save Changes
            </button>
          </form>
        </div>
        
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Notification Preferences
          </h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div>
                <p style={{ fontWeight: '500' }}>Email Notifications</p>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Receive updates via email
                </p>
              </div>
              <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                <input
                  type="checkbox"
                  checked={notifications.email}
                  onChange={() => handleNotificationChange('email')}
                  style={{ opacity: 0, width: 0, height: 0 }}
                />
                <span
                  style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: notifications.email ? '#2563eb' : '#d1d5db',
                    transition: '0.2s',
                    borderRadius: '24px'
                  }}
                >
                  <span
                    style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      transition: '0.2s',
                      borderRadius: '50%',
                      transform: notifications.email ? 'translateX(20px)' : 'translateX(0)',
                      display: 'block'
                    }}
                  ></span>
                </span>
              </label>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <div>
                <p style={{ fontWeight: '500' }}>SMS Notifications</p>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Receive text messages
                </p>
              </div>
              <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                <input
                  type="checkbox"
                  checked={notifications.sms}
                  onChange={() => handleNotificationChange('sms')}
                  style={{ opacity: 0, width: 0, height: 0 }}
                />
                <span
                  style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: notifications.sms ? '#2563eb' : '#d1d5db',
                    transition: '0.2s',
                    borderRadius: '24px'
                  }}
                >
                  <span
                    style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      transition: '0.2s',
                      borderRadius: '50%',
                      transform: notifications.sms ? 'translateX(20px)' : 'translateX(0)',
                      display: 'block'
                    }}
                  ></span>
                </span>
              </label>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <p style={{ fontWeight: '500' }}>Push Notifications</p>
                <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                  Receive push notifications
                </p>
              </div>
              <label style={{ position: 'relative', display: 'inline-block', width: '44px', height: '24px' }}>
                <input
                  type="checkbox"
                  checked={notifications.push}
                  onChange={() => handleNotificationChange('push')}
                  style={{ opacity: 0, width: 0, height: 0 }}
                />
                <span
                  style={{
                    position: 'absolute',
                    cursor: 'pointer',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: notifications.push ? '#2563eb' : '#d1d5db',
                    transition: '0.2s',
                    borderRadius: '24px'
                  }}
                >
                  <span
                    style={{
                      position: 'absolute',
                      height: '16px',
                      width: '16px',
                      left: '4px',
                      bottom: '4px',
                      backgroundColor: 'white',
                      transition: '0.2s',
                      borderRadius: '50%',
                      transform: notifications.push ? 'translateX(20px)' : 'translateX(0)',
                      display: 'block'
                    }}
                  ></span>
                </span>
              </label>
            </div>
          </div>
        </div>
        
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Account Security
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <button
              style={{
                textAlign: 'left',
                backgroundColor: 'white',
                color: '#374151',
                padding: '0.75rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid #d1d5db',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Change Password
            </button>
            
            <button
              style={{
                textAlign: 'left',
                backgroundColor: 'white',
                color: '#374151',
                padding: '0.75rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid #d1d5db',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Two-Factor Authentication
            </button>
            
            <button
              style={{
                textAlign: 'left',
                backgroundColor: '#fef2f2',
                color: '#b91c1c',
                padding: '0.75rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid #fecaca',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;