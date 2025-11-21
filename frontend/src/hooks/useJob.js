import { useState, useEffect } from 'react';
import { api } from '@/services/api';

export const useJob = (jobId) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    const fetchJob = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/jobs/${jobId}`);
        setJob(response.data);
      } catch (err) {
        setError(err);
        setJob(null);
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
  }, [jobId]);

  return { job, loading, error };
};