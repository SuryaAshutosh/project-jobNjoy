import React from 'react';
import { useParams } from 'react-router-dom';
import { useJob } from '@/hooks/useJob';

const JobDetails = () => {
  const { id } = useParams();
  const { job, loading, error } = useJob(id);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading job details...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Error loading job: {error.message}</p>
      </div>
    );
  }

  if (!job) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Job not found</p>
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <button
          onClick={() => window.history.back()}
          style={{
            display: 'flex',
            alignItems: 'center',
            color: '#2563eb',
            background: 'none',
            border: 'none',
            cursor: 'pointer',
            marginBottom: '1rem'
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            style={{ marginRight: '0.5rem' }}
          >
            <line x1="19" y1="12" x2="5" y2="12"></line>
            <polyline points="12 19 5 12 12 5"></polyline>
          </svg>
          Back to Jobs
        </button>
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '1rem'
        }}>
          <div>
            <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
              {job.title}
            </h1>
            <p style={{ fontSize: '1.25rem', color: '#6b7280', marginBottom: '0.25rem' }}>
              {job.company}
            </p>
            <p style={{ color: '#6b7280' }}>
              {job.location} • Posted {new Date(job.created_at).toLocaleDateString()}
            </p>
          </div>
          
          <button
            style={{
              backgroundColor: '#2563eb',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.375rem',
              border: 'none',
              fontWeight: '500',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Apply Now
          </button>
        </div>
      </div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '2fr 1fr', 
        gap: '2rem' 
      }}>
        <div>
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1.5rem', 
            backgroundColor: 'white',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Job Description
            </h2>
            
            <div 
              dangerouslySetInnerHTML={{ __html: job.description }} 
              style={{ lineHeight: '1.6' }}
            />
          </div>
          
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1.5rem', 
            backgroundColor: 'white',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Required Skills
            </h2>
            
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {job.skills?.map((skill, index) => (
                <span
                  key={index}
                  style={{
                    backgroundColor: '#eff6ff',
                    color: '#1d4ed8',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '0.375rem',
                    fontSize: '0.875rem'
                  }}
                >
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
        
        <div>
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1.5rem', 
            backgroundColor: 'white',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
            marginBottom: '1.5rem'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Company Information
            </h2>
            
            <div style={{ marginBottom: '1rem' }}>
              <h3 style={{ fontWeight: '500', marginBottom: '0.25rem' }}>{job.company}</h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                {job.location}
              </p>
            </div>
            
            <p style={{ lineHeight: '1.5' }}>
              No additional company information available.
            </p>
          </div>
          
          <div style={{ 
            border: '1px solid #e5e7eb', 
            borderRadius: '0.5rem', 
            padding: '1.5rem', 
            backgroundColor: 'white',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
          }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Job Details
            </h2>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Salary Range</p>
              <p style={{ color: '#6b7280' }}>{job.salary || 'Not specified'}</p>
            </div>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Location</p>
              <p style={{ color: '#6b7280' }}>{job.location}</p>
            </div>
            
            <div>
              <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Posted</p>
              <p style={{ color: '#6b7280' }}>
                {new Date(job.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetails;