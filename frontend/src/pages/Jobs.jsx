import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Jobs = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [locationFilter, setLocationFilter] = useState('');
  
  // Mock job data
  const mockJobs = [
    {
      id: 1,
      title: 'Senior Software Engineer',
      company: 'Tech Corp',
      location: 'San Francisco, CA',
      salary: '$120,000 - $150,000',
      posted: '2 days ago',
      skills: ['React', 'Node.js', 'Python'],
      description: 'We are looking for a senior software engineer to join our team...'
    },
    {
      id: 2,
      title: 'Product Manager',
      company: 'Innovate Inc',
      location: 'New York, NY',
      salary: '$130,000 - $160,000',
      posted: '1 day ago',
      skills: ['Product Strategy', 'Agile', 'Analytics'],
      description: 'Join our product team to drive innovation and growth...'
    },
    {
      id: 3,
      title: 'UX Designer',
      company: 'Design Studio',
      location: 'Remote',
      salary: '$90,000 - $120,000',
      posted: '3 days ago',
      skills: ['Figma', 'User Research', 'Prototyping'],
      description: 'Create beautiful and intuitive user experiences...'
    }
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setJobs(mockJobs);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredJobs = jobs.filter(job => {
    const matchesSearch = job.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          job.company.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesLocation = locationFilter ? job.location.toLowerCase().includes(locationFilter.toLowerCase()) : true;
    return matchesSearch && matchesLocation;
  });

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem' }}>Job Listings</h1>
        
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
                  <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>{job.salary}</span>
                </div>
                
                <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem', color: '#6b7280' }}>
                  <span>{job.company}</span>
                  <span>•</span>
                  <span>{job.location}</span>
                  <span>•</span>
                  <span>{job.posted}</span>
                </div>
                
                <p style={{ marginBottom: '1rem', color: '#374151' }}>{job.description}</p>
                
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                  {job.skills.map((skill, index) => (
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