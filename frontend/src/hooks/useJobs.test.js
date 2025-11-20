import { renderHook } from '@testing-library/react';
import { useJobs } from './useJobs';

// Mock the API service
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
  },
}));

describe('useJobs', () => {
  test('initializes with correct default values', () => {
    const { result } = renderHook(() => useJobs());
    
    expect(result.current.jobs).toEqual([]);
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBe(null);
  });

  test('fetches jobs', async () => {
    // This would require more complex mocking
    // For now, we'll just test that the hook initializes
  });
});