import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useJobs } from '@/hooks/useJobs';

const Jobs = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [newJobsCount, setNewJobsCount] = useState(0);
  
  // Use real API data with real-time updates
  const { jobs, loading, error, realTimeUpdates } = useJobs({
    keyword: searchTerm,
    location: locationFilter
  });

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          job.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = locationFilter ? job.location.toLowerCase().includes(locationFilter.toLowerCase()) : true;
    return matchesSearch && matchesLocation;
  });

  // Track new jobs for notification
  useEffect(() => {
    if (realTimeUpdates > 0) {
      setNewJobsCount(prev => prev + 1);
    }
  }, [realTimeUpdates]);

  const handleRefreshJobs = () => {
    window.location.reload();
  };

  return (
    <div>
      {/* New jobs notification banner */}
      {newJobsCount > 0 && (
        <div style={{ 
          backgroundColor: '#dcfce7', 
          border: '1px solid #bbf7d0', 
          borderRadius: '0.375rem', 
          padding: '1rem', 
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <strong>{newJobsCount} new job(s) detected!</strong>
            <p>Refresh to see the latest opportunities</p>
          </div>
          <button
            onClick={handleRefreshJobs}
            style={{
              backgroundColor: '#22c55e',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: 'none',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Refresh
          </button>
        </div>
      )}
      
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: '700' }}>Job Listings</h1>
          <Link 
            to="/jobs/real-time"
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              textDecoration: 'none',
              fontWeight: '500'
            }}
          >
            Try Real-Time Jobs
          </Link>
        </div>
        <p style={{ color: '#6b7280' }}>
          Browse job listings with real-time updates
        </p>
        
        <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
          <input
            type="text"
            placeholder="Search jobs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ 
              flex: 1, 
              padding: '0.5rem', 
              borderRadius: '0.375rem', 
              border: '1px solid #d1d5db', 
              fontSize: '0.875rem' 
            }}
          />
          <input
            type="text"
            placeholder="Location"
            value={locationFilter}
            onChange={(e) => setLocationFilter(e.target.value)}
            style={{ 
              flex: 1, 
              padding: '0.5rem', 
              borderRadius: '0.375rem', 
              border: '1px solid #d1d5db', 
              fontSize: '0.875rem' 
            }}
          />
        </div>
      </div>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Loading jobs...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Error loading jobs: {error.message}</p>
        </div>
      ) : (
        <div>
          <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
            Showing {filteredJobs.length} of {jobs.length} jobs
          </p>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {filteredJobs.map(job => (
              <div 
                key={job.id} 
                style={{ 
                  border: '1px solid #e5e7eb', 
                  borderRadius: '0.5rem', 
                  padding: '1.5rem', 
                  backgroundColor: 'white',
                  boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: '600' }}>{job.title}</h2>
                  <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>{job.salary || 'Not specified'}</span>
                </div>
                
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', color: '#6b7280' }}>
                  <span>{job.company}</span>
                  <span>•</span>
                  <span>{job.location}</span>
                  <span>•</span>
                  <span>{new Date(job.created_at).toLocaleDateString()}</span>
                </div>
                
                <p style={{ marginBottom: '1rem', color: '#374151' }}>{job.description}</p>
                
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                  {job.skills?.map((skill, index) => (
                    <span 
                      key={index}
                      style={{ 
                        backgroundColor: '#eff6ff', 
                        color: '#1d4ed8', 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '0.375rem', 
                        fontSize: '0.75rem' 
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Link 
                    to={`/jobs/${job.id}`}
                    style={{ 
                      color: '#2563eb', 
                      textDecoration: 'underline',
                      fontSize: '0.875rem'
                    }}
                  >
                    View Details
                  </Link>
                  <button
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
                    Apply Now
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

export default Jobs;