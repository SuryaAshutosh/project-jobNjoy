import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import ForgotPassword from './pages/ForgotPassword';
import ResetPassword from './pages/ResetPassword';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import RealTimeJobs from './pages/RealTimeJobs';
import JobDetails from './pages/JobDetails';
import Applications from './pages/Applications';
import UploadResume from './pages/UploadResume';
import Settings from './pages/Settings';

const App = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div style={{ display: 'flex', minHeight: '100vh' }}>
            <Sidebar />
            <div style={{ flex: 1, marginLeft: '250px', display: 'flex', flexDirection: 'column' }}>
              <Header />
              <main style={{ flex: 1, padding: '1.5rem', backgroundColor: '#f9fafb' }}>
                <Routes>
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route path="/forgot-password" element={<ForgotPassword />} />
                  <Route path="/reset-password" element={<ResetPassword />} />
                  <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                  <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                  <Route path="/jobs" element={<ProtectedRoute><Jobs /></ProtectedRoute>} />
                  <Route path="/jobs/real-time" element={<ProtectedRoute><RealTimeJobs /></ProtectedRoute>} />
                  <Route path="/jobs/:id" element={<ProtectedRoute><JobDetails /></ProtectedRoute>} />
                  <Route path="/applications" element={<ProtectedRoute><Applications /></ProtectedRoute>} />
                  <Route path="/resume/upload" element={<ProtectedRoute><UploadResume /></ProtectedRoute>} />
                  <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
                </Routes>
              </main>
            </div>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;