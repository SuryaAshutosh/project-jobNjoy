// Create a simple utility function for testing
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

describe('Utility Functions', () => {
  test('formats currency correctly', () => {
    expect(formatCurrency(1000)).toBe('$1,000.00');
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  test('formats date correctly', () => {
    expect(formatDate('2023-06-15')).toBe('Jun 15, 2023');
  });
});

export { formatCurrency, formatDate };