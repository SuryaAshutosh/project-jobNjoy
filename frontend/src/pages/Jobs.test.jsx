import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Jobs from './Jobs';

describe('Jobs', () => {
  test('renders jobs title', () => {
    render(
      <BrowserRouter>
        <Jobs />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Job Listings')).toBeInTheDocument();
  });

  test('renders search input', () => {
    render(
      <BrowserRouter>
        <Jobs />
      </BrowserRouter>
    );
    
    expect(screen.getByPlaceholderText('Search jobs...')).toBeInTheDocument();
  });
});