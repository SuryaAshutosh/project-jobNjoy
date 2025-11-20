import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Applications from './Applications';

describe('Applications', () => {
  test('renders applications title', () => {
    render(
      <BrowserRouter>
        <Applications />
      </BrowserRouter>
    );
    
    expect(screen.getByText('My Applications')).toBeInTheDocument();
  });
});