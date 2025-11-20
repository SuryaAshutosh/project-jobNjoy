import { api } from './api';

describe('API Service', () => {
  test('creates axios instance with correct baseURL', () => {
    expect(api.defaults.baseURL).toBe('http://localhost:8000/api');
  });

  test('sets timeout correctly', () => {
    expect(api.defaults.timeout).toBe(10000);
  });

  test('sets default headers', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });
});