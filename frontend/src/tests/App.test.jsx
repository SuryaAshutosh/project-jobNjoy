import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders jobSee title', () => {
  render(<App />);
  const titleElement = screen.getAllByText(/jobSee/i)[0];
  expect(titleElement).toBeInTheDocument();
});