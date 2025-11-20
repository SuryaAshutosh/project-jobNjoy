import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProtectedRoute from './ProtectedRoute';

// Mock the auth context
vi.mock('@/contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: false,
    isLoading: false,
  }),
}));

describe('ProtectedRoute', () => {
  test('renders loading state when loading', () => {
    // Mock isLoading to true
    vi.mock('@/contexts/AuthContext', () => ({
      useAuth: () => ({
        isAuthenticated: false,
        isLoading: true,
      }),
    }));
    
    render(
      <BrowserRouter>
        <ProtectedRoute>
          <div>Protected Content</div>
        </ProtectedRoute>
      </BrowserRouter>
    );
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });
});