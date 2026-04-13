import type {
  ApiEnvelope,
  ApiErrorEnvelope,
  DailyPatientFlowRow,
  DashboardKpis,
  DemographicSummaryRow,
  DepartmentReferralRow,
  HealthStatus,
} from "../types/api";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:5000";

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") || DEFAULT_API_BASE_URL;

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`);
  const payload = (await response.json().catch(() => ({}))) as
    | ApiEnvelope<T>
    | ApiErrorEnvelope;

  if (!response.ok) {
    const message =
      "error" in payload && payload.error?.message
        ? payload.error.message
        : `API request failed with status ${response.status}.`;
    throw new ApiClientError(message, response.status);
  }

  if (!("data" in payload)) {
    throw new ApiClientError("API response did not include a data payload.");
  }

  return payload.data;
}

export const apiClient = {
  baseUrl: apiBaseUrl,
  getHealth: () => request<HealthStatus>("/health"),
  getKpis: () => request<DashboardKpis>("/api/v1/kpis"),
  getDailyPatientFlow: () =>
    request<DailyPatientFlowRow[]>(
      "/api/v1/daily-patient-flow?order_by=admission_date&limit=1000",
    ),
  getDepartmentReferrals: () =>
    request<DepartmentReferralRow[]>(
      "/api/v1/department-referrals?order_by=total_patient_events&limit=1000",
    ),
  getDemographics: () =>
    request<DemographicSummaryRow[]>(
      "/api/v1/demographics?order_by=total_patient_events&limit=1000",
    ),
};
