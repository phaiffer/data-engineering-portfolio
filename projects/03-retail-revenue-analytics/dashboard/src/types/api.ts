export type ApiErrorEnvelope = {
  error: string;
  message?: string;
  details?: string;
};

export type ListEnvelope<T> = {
  data: T[];
  row_count: number;
  filters: Record<string, unknown>;
};

export type KpiEnvelope = {
  data: DashboardKpis;
  notes: string[];
};

export type HealthStatus = {
  status: "ok" | "degraded" | string;
  project: string;
  api_layer: string;
  database_path: string;
  database_exists: boolean;
};

export type DashboardKpis = {
  total_orders: number | null;
  total_order_items: number | null;
  total_item_revenue: number | null;
  total_freight_value: number | null;
  total_gross_merchandise_value: number | null;
  average_order_value_item_side: number | null;
};

export type DailyRevenueRow = {
  order_purchase_date: string;
  order_status: string;
  order_count: number;
  order_item_count: number;
  item_revenue: number;
  freight_value: number;
  gross_merchandise_value: number;
};

export type CategoryPerformanceRow = {
  product_category_name: string | null;
  product_category_name_english: string | null;
  order_item_count: number;
  item_revenue: number;
  freight_value: number;
  gross_merchandise_value: number;
};

export type SellerPerformanceRow = {
  seller_id: string;
  seller_state: string | null;
  order_item_count: number;
  item_revenue: number;
  freight_value: number;
  gross_merchandise_value: number;
};

export type CustomerStatePerformanceRow = {
  customer_state: string | null;
  order_count: number;
  order_item_count: number;
  item_revenue: number;
  freight_value: number;
  gross_merchandise_value: number;
};

export type OrderStatusSummaryRow = {
  order_status: string;
  order_count: number;
  order_item_count: number;
  item_revenue: number;
  freight_value: number;
  gross_merchandise_value: number;
};

export type PaymentTypeSummaryRow = {
  payment_type: string;
  payment_count: number;
  total_payment_value: number;
  average_payment_value: number;
};

export type SectionResource<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
};

export type DashboardData = {
  health: SectionResource<HealthStatus>;
  kpis: SectionResource<DashboardKpis>;
  dailyRevenue: SectionResource<DailyRevenueRow[]>;
  categoryPerformance: SectionResource<CategoryPerformanceRow[]>;
  sellerPerformance: SectionResource<SellerPerformanceRow[]>;
  customerStatePerformance: SectionResource<CustomerStatePerformanceRow[]>;
  orderStatusSummary: SectionResource<OrderStatusSummaryRow[]>;
  paymentTypeSummary: SectionResource<PaymentTypeSummaryRow[]>;
};
