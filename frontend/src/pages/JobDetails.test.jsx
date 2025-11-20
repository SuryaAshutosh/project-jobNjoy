import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobDetails from './JobDetails';

// Mock useParams hook
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: '1' }),
  };
});

describe('JobDetails', () => {
  test('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <JobDetails />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Loading job details...')).toBeInTheDocument();
  });
});