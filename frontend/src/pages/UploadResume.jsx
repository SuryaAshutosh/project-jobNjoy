import React, { useState, useEffect } from 'react';
import { useResume } from '@/hooks/useResume';

const UploadResume = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const { uploadResume, parseResume, getResumeById, loading: uploading, error } = useResume();
  const [uploaded, setUploaded] = useState(false);
  const [uploadedResumeId, setUploadedResumeId] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [parsingStatus, setParsingStatus] = useState(null);
  const [parsingProgress, setParsingProgress] = useState(0);
  
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
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
  
  const handleUpload = async () => {
    if (!file) return;
    
    try {
      const response = await uploadResume(file);
      setUploaded(true);
      setUploadedResumeId(response.id);
      
      // Trigger parsing after upload
      setParsingStatus('parsing');
      const parseResponse = await parseResume(response.id, { use_llm: true, background: false });
      
      if (parseResponse.status === 'completed') {
        setParsingStatus('completed');
        // Fetch the parsed resume data
        const resumeData = await getResumeById(response.id);
        setParsedData(resumeData.parsed_data);
      } else {
        setParsingStatus('error');
        setParsedData({
          message: "Failed to parse resume. Please try again."
        });
      }
    } catch (err) {
      console.error('Upload failed:', err);
      setParsingStatus('error');
    }
  };
  
  const handleParse = async () => {
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
      
      {error && (
        <div style={{ 
          marginBottom: '1rem', 
          padding: '1rem', 
          backgroundColor: '#fee', 
          border: '1px solid #fecaca', 
          borderRadius: '0.375rem', 
          color: '#c53030' 
        }}>
          Error: {error.message}
        </div>
      )}
      
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
      
      {(uploading || parsingStatus === 'parsing') && (
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
          <p>{uploading ? 'Uploading your resume...' : 'Parsing your resume...'}</p>
          {parsingStatus === 'parsing' && (
            <div style={{ marginTop: '1rem' }}>
              <div style={{
                height: '8px',
                backgroundColor: '#e5e7eb',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${parsingProgress}%`,
                  backgroundColor: '#2563eb',
                  transition: 'width 0.3s ease'
                }}></div>
              </div>
              <p style={{ marginTop: '0.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
                Analyzing your skills and experience...
              </p>
            </div>
          )}
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
            {parsedData.message ? 'Upload Complete' : 'Parsed Resume Data'}
          </h2>
          
          {parsedData.message ? (
            <p>{parsedData.message}</p>
          ) : (
            <>
              {/* Resume Quality Analysis */}
              {parsedData.quality_analysis && (
                <div style={{ 
                  marginBottom: '1rem', 
                  padding: '1rem', 
                  backgroundColor: parsedData.quality_analysis.quality_score > 70 ? '#dcfce7' : '#fef3c7', 
                  border: '1px solid', 
                  borderColor: parsedData.quality_analysis.quality_score > 70 ? '#bbf7d0' : '#fde68a', 
                  borderRadius: '0.375rem' 
                }}>
                  <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>
                    Resume Quality: {parsedData.quality_analysis.quality_score}/100
                  </h3>
                  {parsedData.quality_analysis.suggestions.length > 0 && (
                    <div>
                      <p style={{ fontWeight: '500', marginBottom: '0.25rem' }}>Suggestions for improvement:</p>
                      <ul style={{ paddingLeft: '1.25rem' }}>
                        {parsedData.quality_analysis.suggestions.map((suggestion, index) => (
                          <li key={index} style={{ marginBottom: '0.25rem' }}>{suggestion}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              
              {/* Personal Information */}
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Personal Information</h3>
                {parsedData.personal_info ? (
                  <>
                    <p><strong>Name:</strong> {parsedData.personal_info.name || 'Not extracted'}</p>
                    <p><strong>Email:</strong> {parsedData.personal_info.email || 'Not extracted'}</p>
                    <p><strong>Phone:</strong> {parsedData.personal_info.phone || 'Not extracted'}</p>
                  </>
                ) : (
                  <p>No personal information extracted</p>
                )}
              </div>
              
              {/* Skills */}
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Skills</h3>
                {parsedData.skills && parsedData.skills.length > 0 ? (
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
                ) : (
                  <p>No skills extracted</p>
                )}
              </div>
              
              {/* Experience */}
              <div style={{ marginBottom: '1rem' }}>
                <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Work Experience</h3>
                {parsedData.experience && parsedData.experience.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {parsedData.experience.map((exp, index) => (
                      <div key={index} style={{ padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem' }}>
                        <p style={{ fontWeight: '500' }}>{exp.position || exp.title || 'No title'}</p>
                        <p>{exp.company || 'No company'}</p>
                        <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>{exp.duration || 'No duration'}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No experience extracted</p>
                )}
              </div>
              
              {/* Education */}
              <div>
                <h3 style={{ fontWeight: '500', marginBottom: '0.5rem' }}>Education</h3>
                {parsedData.education && parsedData.education.length > 0 ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    {parsedData.education.map((edu, index) => (
                      <div key={index} style={{ padding: '0.75rem', border: '1px solid #e5e7eb', borderRadius: '0.375rem' }}>
                        <p style={{ fontWeight: '500' }}>{edu.degree || 'No degree'}</p>
                        <p>{edu.institution || 'No institution'}</p>
                        <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>{edu.year || 'No year'}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No education extracted</p>
                )}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default UploadResume;