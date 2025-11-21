import { useState } from 'react';
import { api } from '@/services/api';

export const useUser = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const getCurrentUser = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.get('/auth/me');
      setUser(response.data);
      return response.data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const updateUserProfile = async (userData) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await api.put('/auth/me', userData);
      setUser(response.data);
      return response.data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return {
    user,
    loading,
    error,
    getCurrentUser,
    updateUserProfile
  };
};