export type ApiEnvelope<T> = {
  data: T;
};

export type ApiErrorEnvelope = {
  error?: {
    message?: string;
  };
};

export type HealthStatus = {
  database: string;
  service: string;
  status: string;
  source: string;
};

export type DashboardKpis = {
  total_records: number | null;
  average_salary_usd: number | null;
  median_salary_usd: number | null;
  remote_friendly_share: number | null;
  high_ai_adoption_share: number | null;
  high_automation_risk_share: number | null;
  growth_projection_share: number | null;
};

export type JobTitleSummaryRow = {
  job_title: string;
  total_records: number | null;
  average_salary_usd: number | null;
  median_salary_usd: number | null;
  min_salary_usd: number | null;
  max_salary_usd: number | null;
  remote_friendly_share: number | null;
  high_automation_risk_share: number | null;
  high_ai_adoption_share: number | null;
  growth_projection_share: number | null;
};

export type IndustrySummaryRow = {
  industry: string;
  total_records: number | null;
  average_salary_usd: number | null;
  median_salary_usd: number | null;
  min_salary_usd: number | null;
  max_salary_usd: number | null;
  remote_friendly_share: number | null;
  high_automation_risk_share: number | null;
  high_ai_adoption_share: number | null;
  growth_projection_share: number | null;
};

export type LocationSummaryRow = {
  location: string;
  total_records: number | null;
  average_salary_usd: number | null;
  median_salary_usd: number | null;
  min_salary_usd: number | null;
  max_salary_usd: number | null;
  remote_friendly_share: number | null;
  high_automation_risk_share: number | null;
  high_ai_adoption_share: number | null;
  growth_projection_share: number | null;
};

export type AutomationAiSummaryRow = {
  automation_risk: string;
  ai_adoption_level: string;
  total_records: number | null;
  average_salary_usd: number | null;
  median_salary_usd: number | null;
  remote_friendly_share: number | null;
  growth_projection_share: number | null;
};
