import type {
  ApiErrorEnvelope,
  CategoryPerformanceRow,
  CustomerStatePerformanceRow,
  DailyRevenueRow,
  DashboardKpis,
  HealthStatus,
  KpiEnvelope,
  ListEnvelope,
  OrderStatusSummaryRow,
  PaymentTypeSummaryRow,
  SellerPerformanceRow,
} from "../types/api";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:5002";

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
const apiBaseUrl = normalizeApiBaseUrl(rawApiBaseUrl);
const frontendOrigin =
  typeof window === "undefined" ? "unknown local origin" : window.location.origin;
const apiConfigurationError = getApiConfigurationError(apiBaseUrl);

export class ApiClientError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

function normalizeApiBaseUrl(value: string): string {
  const trimmed = value.trim();
  return (trimmed || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
}

function getApiConfigurationError(value: string): string | null {
  if (
    value === "https://127.0.0.1:5002" ||
    value === "https://localhost:5002"
  ) {
    return [
      `Configured API base URL is ${value}.`,
      "The local Flask API for this project is HTTP-only.",
      "Use http://127.0.0.1:5002 as the browser-facing API URL.",
    ].join(" ");
  }

  return null;
}

function connectionGuidance(errorMessage?: string): string {
  const details = [
    `API not reachable at ${apiBaseUrl}.`,
    `Dashboard origin: ${frontendOrigin}.`,
    "Check whether the Flask API is running.",
    "Check whether the API URL uses http:// rather than https://.",
    "Check whether local CORS allows the current Vite origin.",
  ];

  if (errorMessage) {
    details.push(`Browser fetch detail: ${errorMessage}`);
  }

  return details.join(" ");
}

function buildPath(path: string, query?: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams();
  const cleanPath = normalizeApiPath(path);

  Object.entries(query ?? {}).forEach(([key, value]) => {
    if (value !== undefined) {
      params.set(key, String(value));
    }
  });

  const suffix = params.toString();
  return suffix ? `${cleanPath}?${suffix}` : cleanPath;
}

async function fetchJson<T>(path: string): Promise<T> {
  if (apiConfigurationError) {
    throw new ApiClientError(apiConfigurationError);
  }

  const cleanPath = normalizeApiPath(path);
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${cleanPath}`);
  } catch (error) {
    throw new ApiClientError(
      error instanceof Error
        ? connectionGuidance(error.message)
        : connectionGuidance(),
    );
  }

  const payload = (await response.json().catch(() => ({}))) as T | ApiErrorEnvelope;

  if (!response.ok) {
    const message =
      typeof payload === "object" &&
      payload !== null &&
      "message" in payload &&
      typeof payload.message === "string"
        ? payload.message
        : `API request failed with status ${response.status}.`;
    throw new ApiClientError(message, response.status);
  }

  return payload as T;
}

function assertListEnvelope<T>(payload: ListEnvelope<T>, path: string): T[] {
  if (!Array.isArray(payload.data)) {
    throw new ApiClientError(`Malformed API response from ${path}: expected data array.`);
  }

  return payload.data;
}

function normalizeApiPath(path: string): string {
  const trimmed = path.trim();
  return trimmed.startsWith("/") ? trimmed : `/${trimmed}`;
}

function assertKpiEnvelope(payload: KpiEnvelope): DashboardKpis {
  if (!payload.data || typeof payload.data !== "object") {
    throw new ApiClientError("Malformed API response from /api/v1/kpis.");
  }

  return payload.data;
}

async function requestList<T>(path: string): Promise<T[]> {
  const payload = await fetchJson<ListEnvelope<T>>(path);
  return assertListEnvelope(payload, path);
}

export const apiClient = {
  baseUrl: apiBaseUrl,
  frontendOrigin,
  configurationError: apiConfigurationError,
  getHealth: () => fetchJson<HealthStatus>("/health"),
  getKpis: async () => assertKpiEnvelope(await fetchJson<KpiEnvelope>("/api/v1/kpis")),
  getDailyRevenue: (limit = 180, orderStatus?: string) =>
    requestList<DailyRevenueRow>(
      buildPath("/api/v1/daily-revenue", {
        limit,
        order_status: orderStatus,
        sort: "desc",
      }),
    ),
  getCategoryPerformance: (limit: number) =>
    requestList<CategoryPerformanceRow>(
      buildPath("/api/v1/category-performance", {
        limit,
        sort_by: "gross_merchandise_value",
        sort: "desc",
      }),
    ),
  getSellerPerformance: (limit: number) =>
    requestList<SellerPerformanceRow>(
      buildPath("/api/v1/seller-performance", {
        limit,
        sort_by: "gross_merchandise_value",
        sort: "desc",
      }),
    ),
  getCustomerStatePerformance: (limit: number) =>
    requestList<CustomerStatePerformanceRow>(
      buildPath("/api/v1/customer-state-performance", {
        limit,
        sort_by: "gross_merchandise_value",
        sort: "desc",
      }),
    ),
  getOrderStatusSummary: () =>
    requestList<OrderStatusSummaryRow>("/api/v1/order-status-summary"),
  getPaymentTypeSummary: () =>
    requestList<PaymentTypeSummaryRow>("/api/v1/payment-type-summary"),
};
