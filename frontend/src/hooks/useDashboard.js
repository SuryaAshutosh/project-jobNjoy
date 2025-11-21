import { useState, useEffect } from 'react';
import { api } from '@/services/api';

export const useDashboardStats = () => {
  const [stats, setStats] = useState({
    jobsScraped: 0,
    applicationsSubmitted: 0,
    successRate: 0,
    activeSubscriptions: 0
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await api.get('/dashboard/stats');
        const data = response.data;
        
        setStats({
          jobsScraped: data.jobs_scraped || 0,
          applicationsSubmitted: data.applications_submitted || 0,
          successRate: data.applied_success ? Math.round((data.applied_success / (data.applications_submitted || 1)) * 100) : 0,
          activeSubscriptions: data.user_subscription_status === 'active' ? 1 : 0
        });
      } catch (err) {
        setError(err);
        // Fallback to default values
        setStats({
          jobsScraped: 0,
          applicationsSubmitted: 0,
          successRate: 0,
          activeSubscriptions: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return { stats, loading, error };
};

export const useChartData = () => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChartData = async () => {
      try {
        setLoading(true);
        const response = await api.get('/dashboard/applications/chart');
        const data = response.data;
        
        // Transform data for chart
        const transformedData = (data.labels || []).map((label, index) => ({
          name: label,
          applications: data.data?.[index] || 0
        }));
        
        setChartData(transformedData);
      } catch (err) {
        setError(err);
        setChartData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, []);

  return { chartData, loading, error };
};

export const useTopCompanies = () => {
  const [topCompanies, setTopCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // For now, we'll use static data since there's no specific API endpoint
  // In a real implementation, this would fetch from an API
  useEffect(() => {
    const fetchTopCompanies = async () => {
      try {
        setLoading(true);
        // This would be replaced with an actual API call
        // const response = await api.get('/dashboard/top-companies');
        // setTopCompanies(response.data);
        
        // Temporary static data
        setTopCompanies([
          { company: 'Google', positions: 12 },
          { company: 'Microsoft', positions: 8 },
          { company: 'Amazon', positions: 7 },
          { company: 'Apple', positions: 6 },
          { company: 'Meta', positions: 5 }
        ]);
      } catch (err) {
        setError(err);
        setTopCompanies([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTopCompanies();
  }, []);

  return { topCompanies, loading, error };
};

export const useRecentActivity = () => {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivities = async () => {
      try {
        setLoading(true);
        const response = await api.get('/dashboard/recent-activity');
        const data = response.data;
        
        // Transform activities data
        const transformedActivities = (data.activity || []).map(activity => ({
          id: `${activity.type}-${activity.timestamp}`,
          type: activity.type,
          status: activity.status,
          title: activity.job_title,
          company: activity.company,
          timestamp: activity.timestamp
        }));
        
        setActivities(transformedActivities);
      } catch (err) {
        setError(err);
        setActivities([]);
      } finally {
        setLoading(false);
      }
    };

    fetchActivities();
  }, []);

  return { activities, loading, error };
};