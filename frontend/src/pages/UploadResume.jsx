import React, { useState } from 'react';

const UploadResume = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploaded, setUploaded] = useState(false);
  const [parsedData, setParsedData] = useState(null);
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(true);
  };
  
  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };
  
  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };
  
  const handleUpload = () => {
    if (!file) return;
    
    setUploading(true);
    
    // Simulate file upload and parsing
    setTimeout(() => {
      setUploading(false);
      setUploaded(true);
      
      // Mock parsed data
      setParsedData({
        name: 'John Doe',
        email: 'john.doe@example.com',
        phone: '+1 (555) 123-4567',
        skills: ['React', 'Node.js', 'JavaScript', 'Python', 'SQL'],
        experience: [
          {
            company: 'Tech Corp',
            title: 'Senior Software Engineer',
            duration: '2020 - Present'
          },
          {
            company: 'Startup Inc',
            title: 'Software Developer',
            duration: '2018 - 2020'
          }
        ]
      });
    }, 2000);
  };
  
  const handleParse = () => {
    // In a real app, this would trigger parsing
    console.log('Parsing resume...');
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '1rem' }}>Upload Resume</h1>
        <p style={{ color: '#6b7280' }}>
          Upload your resume to automatically extract your skills and experience
        </p>
      </div>
      
      {!uploaded ? (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          style={{
            border: `2px dashed ${isDragging ? '#2563eb' : '#d1d5db'}`,
            borderRadius: '0.5rem',
            padding: '3rem 2rem',
            textAlign: 'center',
            backgroundColor: isDragging ? '#eff6ff' : '#f9fafb',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
          onClick={() => document.getElementById('file-input').click()}
        >
          <div style={{ marginBottom: '1rem' }}>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="#6b7280"
              strokeWidth="1.5"
              style={{ margin: '0 auto' }}
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="17 8 12 3 7 8"></polyline>
              <line x1="12" y1="3" x2="12" y2="15"></line>
            </svg>
          </div>
          <p style={{ fontSize: '1.125rem', fontWeight: '500', marginBottom: '0.5rem' }}>
            Drag & drop your resume here
          </p>
          <p style={{ color: '#6b7280', marginBottom: '1rem' }}>
            or click to browse files
          </p>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Supported formats: PDF, DOCX, TXT (Max 5MB)
          </p>
          <input
            id="file-input"
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={handleFileChange}
            style={{ display: 'none' }}
          />
        </div>
      ) : null}
      
      {file && !uploaded && (
        <div
          style={{
            marginTop: '1.5rem',
            padding: '1rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.5rem',
            backgroundColor: 'white'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <p style={{ fontWeight: '500' }}>{file.name}</p>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={handleUpload}
              disabled={uploading}
              style={{
                backgroundColor: uploading ? '#9ca3af' : '#2563eb',
                color: 'white',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: 'none',
                fontWeight: '500',
                cursor: uploading ? 'not-allowed' : 'pointer'
              }}
            >
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </div>
      )}
      
      {uploading && (
        <div style={{ marginTop: '1.5rem', textAlign: 'center' }}>
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
          <p>Uploading and parsing your resume...</p>
        </div>
      )}
      
      {parsedData && (
        <div
          style={{
            marginTop: '1.5rem',
            padding: '1.5rem',
            border: '1px solid #d1d5db',
            borderRadius: '0.5rem',
            backgroundColor: 'white'
          }}
        >
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Parsed Resume Data
          </h2>
          
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Personal Information</h3>
            <p><strong>Name:</strong> {parsedData.name}</p>
            <p><strong>Email:</strong> {parsedData.email}</p>
            <p><strong>Phone:</strong> {parsedData.phone}</p>
          </div>
          
          <div style={{ marginBottom: '1rem' }}>
            <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Top Skills</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {parsedData.skills.map((skill, index) => (
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
          
          <div>
            <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Work Experience</h3>
            {parsedData.experience.map((exp, index) => (
              <div key={index} style={{ marginBottom: '0.75rem' }}>
                <p style={{ fontWeight: '500' }}>{exp.title}</p>
                <p>{exp.company} • {exp.duration}</p>
              </div>
            ))}
          </div>
          
          <div style={{ marginTop: '1.5rem', display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={handleParse}
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
              Re-parse Resume
            </button>
            <button
              style={{
                backgroundColor: '#f3f4f6',
                color: '#374151',
                padding: '0.5rem 1rem',
                borderRadius: '0.375rem',
                border: '1px solid #d1d5db',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Edit Information
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadResume;