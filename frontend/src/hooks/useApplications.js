import { useState, useEffect } from 'react';
import { api } from '@/services/api';

export const useApplications = () => {
  const [applications, setApplications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        setLoading(true);
        const response = await api.get('/applications');
        setApplications(response.data);
      } catch (err) {
        setError(err);
        setApplications([]);
      } finally {
        setLoading(false);
      }
    };

    fetchApplications();
  }, []);

  return { applications, loading, error };
};

export const useApplication = (applicationId) => {
  const [application, setApplication] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!applicationId) return;

    const fetchApplication = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/applications/${applicationId}`);
        setApplication(response.data);
      } catch (err) {
        setError(err);
        setApplication(null);
      } finally {
        setLoading(false);
      }
    };

    fetchApplication();
  }, [applicationId]);

  return { application, loading, error };
};