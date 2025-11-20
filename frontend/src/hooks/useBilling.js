import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export const useBilling = () => {
  const [billing, setBilling] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchBilling = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.get('/payments/billing');
      setBilling(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch billing information');
      setBilling(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshBilling = useCallback(async () => {
    await fetchBilling();
  }, [fetchBilling]);

  useEffect(() => {
    fetchBilling();
  }, [fetchBilling]);

  return { billing, loading, error, refreshBilling };
};