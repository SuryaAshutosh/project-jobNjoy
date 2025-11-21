import { api } from './api';

class JobService {
  constructor() {
    this.websocket = null;
    this.listeners = [];
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
  }

  // Subscribe to real-time job updates
  subscribeToJobUpdates(callback) {
    this.listeners.push(callback);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== callback);
    };
  }

  // Connect to WebSocket for real-time updates
  connectToJobUpdates() {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      return;
    }

    try {
      const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/ws/jobs`;
      this.websocket = new WebSocket(wsUrl);

      this.websocket.onopen = () => {
        console.log('Connected to job updates WebSocket');
        this.reconnectAttempts = 0;
      };

      this.websocket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.notifyListeners(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.websocket.onclose = () => {
        console.log('Disconnected from job updates WebSocket');
        this.handleReconnect();
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.websocket.close();
      };
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
      this.handleReconnect();
    }
  }

  // Handle reconnection logic
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 10000); // Exponential backoff
      setTimeout(() => {
        console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connectToJobUpdates();
      }, delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  // Notify all listeners of new data
  notifyListeners(data) {
    this.listeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error('Error notifying listener:', error);
      }
    });
  }

  // Disconnect from WebSocket
  disconnect() {
    if (this.websocket) {
      this.websocket.close();
      this.websocket = null;
    }
    this.listeners = [];
  }

  // Fetch jobs with real-time updates
  async fetchJobs(filters = {}) {
    try {
      const response = await api.get('/jobs', { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch jobs: ${error.message}`);
    }
  }

  // Fetch job by ID
  async fetchJobById(jobId) {
    try {
      const response = await api.get(`/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch job: ${error.message}`);
    }
  }

  // Fetch job sources
  async fetchJobSources() {
    try {
      const response = await api.get('/jobs/sources');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch job sources: ${error.message}`);
    }
  }

  // Trigger job scraping
  async triggerJobScraping(sourceId) {
    try {
      const response = await api.post(`/jobs/scrape?source_id=${sourceId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to trigger job scraping: ${error.message}`);
    }
  }
}

// Export singleton instance
export const jobService = new JobService();