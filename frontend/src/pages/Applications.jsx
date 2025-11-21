import React from 'react';
import { useApplications } from '@/hooks/useApplications';

const Applications = () => {
  const { applications, loading, error } = useApplications();
  
  const getStatusColor = (status) => {
    switch (status) {
      case 'applied':
        return '#3b82f6'; // blue
      case 'interview_scheduled':
        return '#10b981'; // green
      case 'rejected':
        return '#ef4444'; // red
      case 'offer_received':
        return '#8b5cf6'; // purple
      default:
        return '#6b7280'; // gray
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem' }}>My Applications</h1>
      </div>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Loading applications...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Error loading applications: {error.message}</p>
        </div>
      ) : (
        <div>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '1rem' 
          }}>
            {applications.map(app => (
              <div 
                key={app.id} 
                style={{ 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '0.5rem', 
                  padding: '1.5rem', 
                  backgroundColor: 'white',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
                }}
              >
                <div style={{ marginBottom: '1rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '0.25rem' }}>
                    {app.job?.title || 'Unknown Position'}
                  </h2>
                  <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>{app.job?.company || 'Unknown Company'}</p>
                  <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                    Applied on {new Date(app.created_at).toLocaleDateString()}
                  </p>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span 
                    style={{ 
                      padding: '0.25rem 0.5rem', 
                      borderRadius: '0.375rem', 
                      fontSize: '0.75rem', 
                      fontWeight: '500',
                      color: 'white',
                      backgroundColor: getStatusColor(app.status)
                    }}
                  >
                    {app.status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                    via {app.source || 'Unknown'}
                  </span>
                </div>
                
                <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
                  <button
                    style={{
                      flex: 1,
                      backgroundColor: '#f3f4f6',
                      color: '#374151',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      border: '1px solid #d1d5db',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    View Details
                  </button>
                  <button
                    style={{
                      flex: 1,
                      backgroundColor: '#2563eb',
                      color: 'white',
                      padding: '0.5rem',
                      borderRadius: '0.375rem',
                      border: 'none',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Retry
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Applications;