import type {
  ApiEnvelope,
  ApiErrorEnvelope,
  AutomationAiSummaryRow,
  DashboardKpis,
  HealthStatus,
  IndustrySummaryRow,
  JobTitleSummaryRow,
  LocationSummaryRow,
} from "../types/api";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:5001";

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
  getJobTitleSummary: () =>
    request<JobTitleSummaryRow[]>(
      "/api/v1/job-title-summary?order_by=average_salary_usd&limit=8",
    ),
  getIndustrySummary: () =>
    request<IndustrySummaryRow[]>(
      "/api/v1/industry-summary?order_by=total_records&limit=1000",
    ),
  getLocationSummary: () =>
    request<LocationSummaryRow[]>(
      "/api/v1/location-summary?order_by=average_salary_usd&limit=8",
    ),
  getAutomationAiSummary: () =>
    request<AutomationAiSummaryRow[]>(
      "/api/v1/automation-ai-summary?order_by=total_records&limit=1000",
    ),
};
