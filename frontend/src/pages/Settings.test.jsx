import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Settings from './Settings';

describe('Settings', () => {
  test('renders settings title', () => {
    render(
      <BrowserRouter>
        <Settings />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  test('renders profile information section', () => {
    render(
      <BrowserRouter>
        <Settings />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Profile Information')).toBeInTheDocument();
  });
});