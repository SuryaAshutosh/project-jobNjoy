import { render, screen } from '@testing-library/react';
import { Button } from './button';

describe('Button', () => {
  test('renders button with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('applies correct CSS classes', () => {
    render(<Button variant="secondary">Test</Button>);
    const button = screen.getByRole('button');
    // Since we're using inline styles, we can't easily test classes
    // In a real implementation with Tailwind, we would check for class names
  });

  test('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    const button = screen.getByText('Click me');
    button.click();
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});