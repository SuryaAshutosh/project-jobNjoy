import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [stats, setStats] = useState({
    jobsScraped: 1247,
    applicationsSubmitted: 86,
    successRate: 23,
    activeSubscriptions: 1
  });
  
  const [chartData, setChartData] = useState([
    { name: 'Jan', applications: 12 },
    { name: 'Feb', applications: 19 },
    { name: 'Mar', applications: 15 },
    { name: 'Apr', applications: 22 },
    { name: 'May', applications: 18 },
    { name: 'Jun', applications: 25 }
  ]);
  
  const [topCompanies, setTopCompanies] = useState([
    { company: 'Google', positions: 12 },
    { company: 'Microsoft', positions: 8 },
    { company: 'Amazon', positions: 7 },
    { company: 'Apple', positions: 6 },
    { company: 'Meta', positions: 5 }
  ]);

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>
          Dashboard
        </h1>
        <p style={{ color: '#6b7280' }}>
          Welcome back! Here's what's happening with your job search.
        </p>
      </div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', 
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div style={{ 
              width: '36px', 
              height: '36px', 
              borderRadius: '0.5rem', 
              backgroundColor: '#dbeafe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '0.75rem'
            }}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#2563eb"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
            <h3 style={{ fontWeight: '500', color: '#6b7280' }}>Jobs Scraped</h3>
          </div>
          <p style={{ fontSize: '1.5rem', fontWeight: '600' }}>{stats.jobsScraped.toLocaleString()}</p>
        </div>
        
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div style={{ 
              width: '36px', 
              height: '36px', 
              borderRadius: '0.5rem', 
              backgroundColor: '#dcfce7',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '0.75rem'
            }}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#10b981"
                strokeWidth="2"
              >
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10 9 9 9 8 9"></polyline>
              </svg>
            </div>
            <h3 style={{ fontWeight: '500', color: '#6b7280' }}>Applications</h3>
          </div>
          <p style={{ fontSize: '1.5rem', fontWeight: '600' }}>{stats.applicationsSubmitted}</p>
        </div>
        
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div style={{ 
              width: '36px', 
              height: '36px', 
              borderRadius: '0.5rem', 
              backgroundColor: '#ffedd5',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '0.75rem'
            }}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#f59e0b"
                strokeWidth="2"
              >
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M12 6v6l4 2"></path>
              </svg>
            </div>
            <h3 style={{ fontWeight: '500', color: '#6b7280' }}>Success Rate</h3>
          </div>
          <p style={{ fontSize: '1.5rem', fontWeight: '600' }}>{stats.successRate}%</p>
        </div>
        
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '0.5rem' }}>
            <div style={{ 
              width: '36px', 
              height: '36px', 
              borderRadius: '0.5rem', 
              backgroundColor: '#ede9fe',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '0.75rem'
            }}>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="#8b5cf6"
                strokeWidth="2"
              >
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
              </svg>
            </div>
            <h3 style={{ fontWeight: '500', color: '#6b7280' }}>Subscriptions</h3>
          </div>
          <p style={{ fontSize: '1.5rem', fontWeight: '600' }}>{stats.activeSubscriptions}</p>
        </div>
      </div>
      
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: '2fr 1fr', 
        gap: '1.5rem',
        marginBottom: '2rem'
      }}>
        <div style={{ 
          border: '1px solid #e5e7eb', 
          borderRadius: '0.5rem', 
          padding: '1.5rem', 
          backgroundColor: 'white',
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
        }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            Applications Over Time
          </h2>
          
          <div style={{ 
            height: '300px', 
            display: 'flex', 
            alignItems: 'flex-end', 
            gap: '0.5rem',
            padding: '1rem 0'
          }}>
            {chartData.map((item, index) => (
              <div key={index} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div
                  style={{
                    width: '100%',
                    backgroundColor: '#3b82f6',
                    borderRadius: '0.25rem',
                    height: `${(item.applications / 30) * 100}%`,
                    minHeight: '4px',
                    transition: 'height 0.3s ease'
                  }}
                ></div>
                <span style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#6b7280' }}>
                  {item.name}
                </span>
              </div>
            ))}
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
            Top Companies Hiring
          </h2>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {topCompanies.map((company, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: '500' }}>{company.company}</span>
                <span 
                  style={{ 
                    backgroundColor: '#eff6ff', 
                    color: '#1d4ed8', 
                    padding: '0.25rem 0.5rem', 
                    borderRadius: '0.375rem', 
                    fontSize: '0.75rem' 
                  }}
                >
                  {company.positions} positions
                </span>
              </div>
            ))}
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
          Recent Activity
        </h2>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: '#10b981',
              marginRight: '0.75rem'
            }}></div>
            <div>
              <p style={{ fontWeight: '500' }}>Application submitted for Senior Software Engineer at Google</p>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>2 hours ago</p>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: '#3b82f6',
              marginRight: '0.75rem'
            }}></div>
            <div>
              <p style={{ fontWeight: '500' }}>Resume parsed successfully</p>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>1 day ago</p>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              width: '8px', 
              height: '8px', 
              borderRadius: '50%', 
              backgroundColor: '#f59e0b',
              marginRight: '0.75rem'
            }}></div>
            <div>
              <p style={{ fontWeight: '500' }}>Interview scheduled with Microsoft</p>
              <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>3 days ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;