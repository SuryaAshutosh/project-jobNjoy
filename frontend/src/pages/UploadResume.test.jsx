import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import UploadResume from './UploadResume';

describe('UploadResume', () => {
  test('renders upload resume title', () => {
    render(
      <BrowserRouter>
        <UploadResume />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Upload Resume')).toBeInTheDocument();
  });

  test('renders drag and drop area', () => {
    render(
      <BrowserRouter>
        <UploadResume />
      </BrowserRouter>
    );
    
    expect(screen.getByText('Drag & drop your resume here')).toBeInTheDocument();
  });
});