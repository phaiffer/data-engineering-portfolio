export interface ApiEnvelope<T> {
  data: T;
}

export interface ApiErrorEnvelope {
  error?: {
    message?: string;
  };
}

export interface HealthStatus {
  service: string;
  status: string;
}

export interface DashboardKpis {
  total_patient_events?: number | null;
  average_waittime_overall?: number | null;
  average_satisfaction_overall?: number | null;
  number_of_daily_points?: number | null;
  number_of_department_groups?: number | null;
  number_of_demographic_groups?: number | null;
}

export interface DailyPatientFlowRow {
  admission_date: string | null;
  total_patient_events: number | null;
  average_patient_waittime: number | null;
  average_patient_satisfaction_score: number | null;
  admitted_patient_events: number | null;
  null_department_referral_events: number | null;
  null_satisfaction_score_events: number | null;
}

export interface DepartmentReferralRow {
  department_referral: string | null;
  total_patient_events: number | null;
  average_patient_waittime: number | null;
  average_patient_satisfaction_score: number | null;
  share_of_total_events: number | null;
}

export interface DemographicSummaryRow {
  patient_gender: string | null;
  patient_race: string | null;
  patient_age_band: string | null;
  total_patient_events: number | null;
  average_patient_waittime: number | null;
  average_patient_satisfaction_score: number | null;
}

