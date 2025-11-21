import { useState, useEffect } from 'react';
import { resumeService } from '@/services/resumeService';

export const useResume = () => {
  const [resumes, setResumes] = useState([]);
  const [currentResume, setCurrentResume] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all resumes for the user
  const fetchResumes = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.getUserResumes();
      setResumes(data);
    } catch (err) {
      setError(err);
    } finally {
      setLoading(false);
    }
  };

  // Upload a new resume
  const uploadResume = async (file) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.uploadResume(file);
      // Refresh the resumes list
      await fetchResumes();
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get a specific resume by ID
  const getResumeById = async (resumeId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.getResumeById(resumeId);
      setCurrentResume(data);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Parse a resume
  const parseResume = async (resumeId, options) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.parseResume(resumeId, options);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Delete a resume
  const deleteResume = async (resumeId) => {
    try {
      setLoading(true);
      setError(null);
      await resumeService.deleteResume(resumeId);
      // Refresh the resumes list
      await fetchResumes();
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Validate/correct resume data
  const validateResume = async (resumeId, corrections, userId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.validateResume(resumeId, corrections, userId);
      // Refresh the current resume
      await getResumeById(resumeId);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Get resume for review
  const getResumeForReview = async (resumeId) => {
    try {
      setLoading(true);
      setError(null);
      const data = await resumeService.getResumeForReview(resumeId);
      return data;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Initialize by fetching resumes
  useEffect(() => {
    fetchResumes();
  }, []);

  return {
    resumes,
    currentResume,
    loading,
    error,
    fetchResumes,
    uploadResume,
    getResumeById,
    parseResume,
    deleteResume,
    validateResume,
    getResumeForReview
  };
};