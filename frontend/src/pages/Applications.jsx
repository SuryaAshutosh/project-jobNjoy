import React, { useState, useEffect } from 'react';

const Applications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Mock application data
  const mockApplications = [
    {
      id: 1,
      jobTitle: 'Senior Software Engineer',
      company: 'Tech Corp',
      appliedAt: '2023-06-15',
      status: 'Submitted',
      source: 'LinkedIn'
    },
    {
      id: 2,
      jobTitle: 'Product Manager',
      company: 'Innovate Inc',
      appliedAt: '2023-06-10',
      status: 'Interview Scheduled',
      source: 'Company Website'
    },
    {
      id: 3,
      jobTitle: 'UX Designer',
      company: 'Design Studio',
      appliedAt: '2023-06-05',
      status: 'Rejected',
      source: 'Job Board'
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setApplications(mockApplications);
      setLoading(false);
    }, 1000);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'Submitted':
        return '#3b82f6'; // blue
      case 'Interview Scheduled':
        return '#10b981'; // green
      case 'Rejected':
        return '#ef4444'; // red
      case 'Offer Received':
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
                    {app.jobTitle}
                  </h2>
                  <p style={{ color: '#6b7280', marginBottom: '0.5rem' }}>{app.company}</p>
                  <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                    Applied on {new Date(app.appliedAt).toLocaleDateString()}
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
                    {app.status}
                  </span>
                  <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                    via {app.source}
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