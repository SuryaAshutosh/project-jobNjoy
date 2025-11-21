import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobService } from '@/services/jobService';

const RealTimeJobs = () => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newJobsCount, setNewJobsCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  // Fetch initial jobs
  useEffect(() => {
    const fetchInitialJobs = async () => {
      try {
        setLoading(true);
        const data = await jobService.fetchJobs();
        setJobs(data);
        setFilteredJobs(data);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialJobs();
  }, []);

  // Connect to real-time updates
  useEffect(() => {
    // Connect to WebSocket
    jobService.connectToJobUpdates();
    setIsConnected(true);

    // Subscribe to job updates
    const unsubscribe = jobService.subscribeToJobUpdates((data) => {
      if (data.type === 'job_update') {
        // Add new job to the list
        setJobs(prevJobs => {
          const updatedJobs = [data.data, ...prevJobs];
          // Apply current filters to new job list
          const filtered = updatedJobs.filter(job => {
            const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                                job.company.toLowerCase().includes(searchTerm.toLowerCase());
            const matchesLocation = locationFilter ? job.location.toLowerCase().includes(locationFilter.toLowerCase()) : true;
            return matchesSearch && matchesLocation;
          });
          setFilteredJobs(filtered);
          return updatedJobs;
        });
        setNewJobsCount(prev => prev + 1);
      }
    });

    // Cleanup
    return () => {
      unsubscribe();
      jobService.disconnect();
    };
  }, [searchTerm, locationFilter]);

  // Apply filters when they change
  useEffect(() => {
    const filtered = jobs.filter(job => {
      const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          job.company.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesLocation = locationFilter ? job.location.toLowerCase().includes(locationFilter.toLowerCase()) : true;
      return matchesSearch && matchesLocation;
    });
    setFilteredJobs(filtered);
  }, [searchTerm, locationFilter, jobs]);

  const handleRefreshJobs = () => {
    window.location.reload();
  };

  const handleClearNewJobs = () => {
    setNewJobsCount(0);
  };

  return (
    <div>
      {/* Connection status indicator */}
      <div style={{ 
        marginBottom: '1rem', 
        padding: '0.5rem', 
        backgroundColor: isConnected ? '#dcfce7' : '#fee', 
        border: '1px solid', 
        borderColor: isConnected ? '#bbf7d0' : '#fecaca', 
        borderRadius: '0.375rem', 
        textAlign: 'center'
      }}>
        <span style={{ fontSize: '0.875rem' }}>
          {isConnected ? (
            <span style={{ color: '#166534' }}>✓ Connected to real-time job updates</span>
          ) : (
            <span style={{ color: '#c53030' }}>⚠ Disconnected from real-time updates</span>
          )}
        </span>
      </div>

      {/* New jobs notification banner */}
      {newJobsCount > 0 && (
        <div style={{ 
          backgroundColor: '#dbeafe', 
          border: '1px solid #bfdbfe', 
          borderRadius: '0.375rem', 
          padding: '1rem', 
          marginBottom: '1rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <strong>{newJobsCount} new job(s) detected!</strong>
            <p>Real-time updates are working correctly</p>
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={handleClearNewJobs}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: 'none',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Clear
            </button>
          </div>
        </div>
      )}

      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem' }}>Real-Time Job Board</h1>
        <p style={{ color: '#6b7280' }}>
          Live job listings updated in real-time as they become available
        </p>
      </div>

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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <div style={{ marginBottom: '1rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              border: '4px solid #e5e7eb',
              borderTop: '4px solid #2563eb',
              borderRadius: '50%',
              margin: '0 auto',
              animation: 'spin 1s linear infinite'
            }}></div>
          </div>
          <p>Loading real-time job listings...</p>
        </div>
      ) : error ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p>Error loading jobs: {error.message}</p>
          <button
            onClick={handleRefreshJobs}
            style={{
              marginTop: '1rem',
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '0.5rem 1rem',
              borderRadius: '0.375rem',
              border: 'none',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      ) : (
        <div>
          <p style={{ marginBottom: '1rem', color: '#6b7280' }}>
            Showing {filteredJobs.length} of {jobs.length} jobs
          </p>

          {filteredJobs.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2rem', color: '#6b7280' }}>
              <p>No jobs found matching your criteria</p>
              <button
                onClick={() => {
                  setSearchTerm('');
                  setLocationFilter('');
                }}
                style={{
                  marginTop: '1rem',
                  backgroundColor: '#f3f4f6',
                  color: '#374151',
                  padding: '0.5rem 1rem',
                  borderRadius: '0.375rem',
                  border: '1px solid #d1d5db',
                  fontWeight: '500',
                  cursor: 'pointer'
                }}
              >
                Clear filters
              </button>
            </div>
          ) : (
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
                    <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>{job.salary_range || 'Not specified'}</span>
                  </div>

                  <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', color: '#6b7280' }}>
                    <span>{job.company}</span>
                    <span>•</span>
                    <span>{job.location}</span>
                    <span>•</span>
                    <span>{job.created_at ? new Date(job.created_at).toLocaleDateString() : 'Unknown date'}</span>
                  </div>

                  <p style={{ marginBottom: '1rem', color: '#374151' }}>
                    {job.description ? job.description.substring(0, 200) + '...' : 'No description available'}
                  </p>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                    {job.skills?.slice(0, 5).map((skill, index) => (
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
                    {job.skills && job.skills.length > 5 && (
                      <span style={{ 
                        backgroundColor: '#f3f4f6', 
                        color: '#6b7280', 
                        padding: '0.25rem 0.5rem', 
                        borderRadius: '0.375rem', 
                        fontSize: '0.75rem' 
                      }}>
                        +{job.skills.length - 5} more
                      </span>
                    )}
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
          )}
        </div>
      )}
    </div>
  );
};

export default RealTimeJobs;