import { useState, useEffect, useRef } from 'react';
import { jobService } from '@/services/jobService';

export const useJobs = (filters = {}) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [realTimeUpdates, setRealTimeUpdates] = useState(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        const data = await jobService.fetchJobs(filters);
        if (mountedRef.current) {
          setJobs(data);
        }
      } catch (err) {
        if (mountedRef.current) {
          setError(err);
        }
      } finally {
        if (mountedRef.current) {
          setLoading(false);
        }
      }
    };

    fetchJobs();
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    // Connect to real-time updates
    jobService.connectToJobUpdates();
    
    // Subscribe to job updates
    const unsubscribe = jobService.subscribeToJobUpdates((data) => {
      if (data.type === 'job_update' && mountedRef.current) {
        setRealTimeUpdates(prev => prev + 1);
        // In a real implementation, you might want to add the new job to the list
        // or update existing jobs
      }
    });

    // Cleanup function
    return () => {
      mountedRef.current = false;
      unsubscribe();
    };
  }, []);

  return { jobs, loading, error, realTimeUpdates };
};