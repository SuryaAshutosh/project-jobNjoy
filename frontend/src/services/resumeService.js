import { api } from './api';

class ResumeService {
  constructor() {
    this.websocket = null;
    this.parsingListeners = [];
  }

  // Upload a resume file
  async uploadResume(file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post('/resume/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      return response.data;
    } catch (error) {
      throw new Error(`Failed to upload resume: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Trigger resume parsing
  async parseResume(resumeId, options = {}) {
    try {
      const defaultOptions = {
        use_llm: true,
        generate_vectors: false,
        background: true
      };
      
      const parseOptions = { ...defaultOptions, ...options };
      
      const response = await api.post(`/resume/${resumeId}/parse`, parseOptions);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to parse resume: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Get resume by ID
  async getResumeById(resumeId) {
    try {
      const response = await api.get(`/resume/${resumeId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch resume: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Get all resumes for user
  async getUserResumes() {
    try {
      const response = await api.get('/resume/');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch resumes: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Delete a resume
  async deleteResume(resumeId) {
    try {
      const response = await api.delete(`/resume/${resumeId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to delete resume: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Validate/correct resume data
  async validateResume(resumeId, corrections, userId) {
    try {
      const requestData = {
        corrections,
        user_id: userId
      };
      
      const response = await api.post(`/resume/validate/${resumeId}`, requestData);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to validate resume: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Get resume for review
  async getResumeForReview(resumeId) {
    try {
      const response = await api.get(`/resume/review/${resumeId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get resume for review: ${error.response?.data?.detail || error.message}`);
    }
  }

  // Subscribe to parsing updates
  subscribeToParsingUpdates(callback) {
    this.parsingListeners.push(callback);
    return () => {
      this.parsingListeners = this.parsingListeners.filter(listener => listener !== callback);
    };
  }

  // Notify parsing listeners
  notifyParsingListeners(data) {
    this.parsingListeners.forEach(listener => {
      try {
        listener(data);
      } catch (error) {
        console.error('Error notifying parsing listener:', error);
      }
    });
  }
}

// Export singleton instance
export const resumeService = new ResumeService();