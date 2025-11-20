import { render, screen } from '@testing-library/react';
import App from '../App';

test('renders JobCopilot title', () => {
  render(<App />);
  const titleElement = screen.getAllByText(/JobCopilot/i)[0];
  expect(titleElement).toBeInTheDocument();
});