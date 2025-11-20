import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const JobDetails = () => {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  
  // Mock job data
  const mockJob = {
    id: id,
    title: 'Senior Software Engineer',
    company: 'Tech Corp',
    location: 'San Francisco, CA',
    salary: '$120,000 - $150,000',
    posted: '2023-06-15',
    skills: ['React', 'Node.js', 'Python', 'AWS', 'Docker'],
    description: `
      <p>We are looking for a talented Senior Software Engineer to join our engineering team. In this role, you will be responsible for designing, developing, and maintaining scalable web applications.</p>
      
      <h3>Responsibilities</h3>
      <ul>
        <li>Design and implement scalable web applications using modern technologies</li>
        <li>Collaborate with cross-functional teams to define, design, and ship new features</li>
        <li>Write clean, maintainable, and testable code</li>
        <li>Participate in code reviews and contribute to team knowledge sharing</li>
        <li>Troubleshoot, debug, and optimize application performance</li>
      </ul>
      
      <h3>Requirements</h3>
      <ul>
        <li>Bachelor's degree in Computer Science or related field</li>
        <li>5+ years of experience in software development</li>
        <li>Strong proficiency in JavaScript, HTML, and CSS</li>
        <li>Experience with React and Node.js</li>
        <li>Familiarity with cloud platforms (AWS, GCP, or Azure)</li>
        <li>Knowledge of containerization technologies (Docker, Kubernetes)</li>
      </ul>
      
      <h3>Benefits</h3>
      <ul>
        <li>Competitive salary and equity package</li>
        <li>Comprehensive health, dental, and vision insurance</li>
        <li>Flexible work arrangements</li>
        <li>Professional development opportunities</li>
        <li>Generous PTO and parental leave</li>
      </ul>
    `,
    companyInfo: {
      name: 'Tech Corp',
      description: 'Tech Corp is a leading technology company focused on building innovative solutions for the future.',
      size: '1000-5000 employees',
      industry: 'Software Development',
      headquarters: 'San Francisco, CA'
    }
  };

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setJob(mockJob);
      setLoading(false);
    }, 1000);
  }, [id]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <p>Loading job details...</p>
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
              {job.location} • Posted {new Date(job.posted).toLocaleDateString()}
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
              {job.skills.map((skill, index) => (
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
              <h3 style={{ fontWeight: '500', marginBottom: '0.25rem' }}>{job.companyInfo.name}</h3>
              <p style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                {job.companyInfo.industry}
              </p>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                {job.companyInfo.size} • {job.companyInfo.headquarters}
              </p>
            </div>
            
            <p style={{ lineHeight: '1.5' }}>
              {job.companyInfo.description}
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
              <p style={{ color: '#6b7280' }}>{job.salary}</p>
            </div>
            
            <div style={{ marginBottom: '0.75rem' }}>
              <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Location</p>
              <p style={{ color: '#6b7280' }}>{job.location}</p>
            </div>
            
            <div>
              <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Posted</p>
              <p style={{ color: '#6b7280' }}>
                {new Date(job.posted).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetails;