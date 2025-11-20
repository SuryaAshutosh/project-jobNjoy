// User types
export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  subscription_status: string;
  created_at: string;
  updated_at: string;
}

// Resume types
export interface Resume {
  id: string;
  user_id: string;
  file_url: string;
  raw_text: string;
  parsed_data: EnhancedResumeData | null;
  created_at: string;
}

export interface SkillEntry {
  skill: string;
  confidence: number;
  source: string;
}

export interface ExperienceEntry {
  company: string;
  title: string;
  start_date: string | null;
  end_date: string | null;
  bullets: string[];
  duration_months: number | null;
  confidence: number;
}

export interface EducationEntry {
  institution: string;
  degree: string | null;
  start_date: string | null;
  end_date: string | null;
  confidence: number;
}

export interface EnhancedResumeData {
  resume_id: string | null;
  name: string;
  emails: string[];
  phones: string[];
  urls: string[];
  linkedin: string | null;
  github: string | null;
  summary: string;
  skills: SkillEntry[];
  experiences: ExperienceEntry[];
  education: EducationEntry[];
  certifications: string[];
  languages: string[];
  locations: string[];
  raw_text: string;
  ocr_used: boolean;
  parsing_confidence: number;
  generated_at: string;
  provenance: Record<string, any>;
}

// Job types
export interface Job {
  id: string;
  title: string;
  company: string;
  url: string;
  description: string;
  skills: string[];
  salary_range: string | null;
  location: string | null;
  source_id: string;
  created_at: string;
}

export interface JobSource {
  id: string;
  name: string;
  base_url: string;
  created_at: string;
}

// Application types
export interface Application {
  id: string;
  user_id: string;
  job_id: string;
  status: string;
  notes: string | null;
  applied_at: string | null;
  created_at: string;
}

// Dashboard types
export interface DashboardStats {
  jobs_scraped: number;
  applications_submitted: number;
  applied_success: number;
  pending_applications: number;
  failed_applications: number;
  user_subscription_status: string;
}

export interface ChartData {
  labels: string[];
  data: number[];
}