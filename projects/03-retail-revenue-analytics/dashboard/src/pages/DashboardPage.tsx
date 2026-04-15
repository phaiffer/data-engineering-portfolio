import { useMemo, useState } from "react";
import { DailyRevenueChart } from "../components/charts/DailyRevenueChart";
import {
  RevenueBarChart,
  type RevenueBarPoint,
} from "../components/charts/RevenueBarChart";
import {
  SummaryBarChart,
  type SummaryBarPoint,
} from "../components/charts/SummaryBarChart";
import { KpiCard } from "../components/KpiCard";
import { SectionCard } from "../components/SectionCard";
import { SectionResource } from "../components/SectionResource";
import { RankedTable } from "../components/tables/RankedTable";
import { useDashboardData } from "../hooks/useDashboardData";
import {
  formatCurrency,
  formatDate,
  formatInteger,
  formatLabel,
} from "../lib/format";
import { apiClient } from "../services/api";
import type {
  CategoryPerformanceRow,
  CustomerStatePerformanceRow,
  DailyRevenueRow,
  DashboardKpis,
  OrderStatusSummaryRow,
  PaymentTypeSummaryRow,
  SellerPerformanceRow,
} from "../types/api";

const topNOptions = [5, 10, 15];
const dailyStatusOptions = ["delivered", "shipped", "invoiced", "processing", "canceled", ""];

export function DashboardPage() {
  const [topN, setTopN] = useState(10);
  const [dailyOrderStatus, setDailyOrderStatus] = useState("delivered");
  const [refreshKey, setRefreshKey] = useState(0);
  const dashboard = useDashboardData(topN, dailyOrderStatus, refreshKey);

  const isApiHealthy = dashboard.health.data?.status === "ok" && !dashboard.health.error;
  const healthLabel = dashboard.health.isLoading
    ? "Checking API"
    : isApiHealthy
      ? "API connected"
      : "API unavailable";

  return (
    <main className="app-shell">
      <header className="page-header">
        <div className="page-header__copy">
          <span className="eyebrow">Local analytics dashboard</span>
          <h1>Retail Revenue Analytics</h1>
          <p>
            Portfolio dashboard over the read-only Flask API and DBT DuckDB marts for the
            Olist retail dataset.
          </p>
          <div className="note-row" aria-label="Dashboard scope notes">
            <span>Metrics are local analytical outputs over Olist data.</span>
            <span>Revenue is item-side and not accounting-grade.</span>
            <span>Payments describe payment behavior, not item-level revenue.</span>
          </div>
        </div>
        <div className="header-panel">
          <div className={`status-pill ${isApiHealthy ? "status-pill--ok" : "status-pill--bad"}`}>
            <span aria-hidden="true" />
            {healthLabel}
          </div>
          <dl>
            <div>
              <dt>API base URL</dt>
              <dd>{apiClient.baseUrl}</dd>
            </div>
            <div>
              <dt>Read path</dt>
              <dd>DuckDB marts through Flask</dd>
            </div>
          </dl>
          <button type="button" onClick={() => setRefreshKey((value) => value + 1)}>
            Refresh data
          </button>
        </div>
      </header>

      <section className="toolbar" aria-label="Dashboard controls">
        <label>
          Daily trend status
          <select
            value={dailyOrderStatus}
            onChange={(event) => setDailyOrderStatus(event.target.value)}
          >
            {dailyStatusOptions.map((option) => (
              <option value={option} key={option || "all"}>
                {option ? formatLabel(option) : "All statuses"}
              </option>
            ))}
          </select>
        </label>
        <label>
          Top ranked rows
          <select
            value={topN}
            onChange={(event) => setTopN(Number(event.target.value))}
          >
            {topNOptions.map((option) => (
              <option value={option} key={option}>
                Top {option}
              </option>
            ))}
          </select>
        </label>
      </section>

      <KpiSection kpis={dashboard.kpis} />

      <SectionCard
        title="Daily Revenue Trend"
        eyebrow="/api/v1/daily-revenue"
        description="Daily item revenue and gross merchandise value from the modeled revenue mart, filtered by the selected order status."
      >
        <SectionResource
          resource={dashboard.dailyRevenue}
          loadingMessage="Loading daily revenue..."
          emptyMessage="The daily revenue endpoint returned no rows."
        >
          {(rows) => <DailyRevenueSection rows={rows} orderStatus={dailyOrderStatus} />}
        </SectionResource>
      </SectionCard>

      <div className="section-grid">
        <SectionCard
          title="Top Categories"
          eyebrow="/api/v1/category-performance"
          description="Product categories ranked by gross merchandise value."
        >
          <SectionResource
            resource={dashboard.categoryPerformance}
            loadingMessage="Loading category performance..."
            emptyMessage="The category performance endpoint returned no rows."
          >
            {(rows) => <CategorySection rows={rows} />}
          </SectionResource>
        </SectionCard>

        <SectionCard
          title="Top Sellers"
          eyebrow="/api/v1/seller-performance"
          description="Seller performance ranked by item-side GMV with state context."
        >
          <SectionResource
            resource={dashboard.sellerPerformance}
            loadingMessage="Loading seller performance..."
            emptyMessage="The seller performance endpoint returned no rows."
          >
            {(rows) => <SellerSection rows={rows} />}
          </SectionResource>
        </SectionCard>

        <SectionCard
          title="Customer States"
          eyebrow="/api/v1/customer-state-performance"
          description="Customer geography performance using customer state and item-side measures."
        >
          <SectionResource
            resource={dashboard.customerStatePerformance}
            loadingMessage="Loading customer state performance..."
            emptyMessage="The customer state performance endpoint returned no rows."
          >
            {(rows) => <CustomerStateSection rows={rows} />}
          </SectionResource>
        </SectionCard>

        <SectionCard
          title="Order Status"
          eyebrow="/api/v1/order-status-summary"
          description="Order counts and item-side GMV retained by status."
        >
          <SectionResource
            resource={dashboard.orderStatusSummary}
            loadingMessage="Loading order status summary..."
            emptyMessage="The order status endpoint returned no rows."
          >
            {(rows) => <OrderStatusSection rows={rows} />}
          </SectionResource>
        </SectionCard>

        <SectionCard
          title="Payment Type"
          eyebrow="/api/v1/payment-type-summary"
          description="Payment count, payment value, and average payment value by payment type."
        >
          <SectionResource
            resource={dashboard.paymentTypeSummary}
            loadingMessage="Loading payment type summary..."
            emptyMessage="The payment type endpoint returned no rows."
          >
            {(rows) => <PaymentTypeSection rows={rows} />}
          </SectionResource>
        </SectionCard>
      </div>
    </main>
  );
}

function KpiSection({
  kpis,
}: {
  kpis: {
    data: DashboardKpis | null;
    error: string | null;
    isLoading: boolean;
  };
}) {
  return (
    <section className="kpi-grid" aria-label="Retail KPI cards">
      <SectionResource
        resource={kpis}
        loadingMessage="Loading KPI cards..."
        emptyMessage="The KPI endpoint returned no data."
      >
        {(data) => (
          <>
            <KpiCard
              label="Total orders"
              value={formatInteger(data.total_orders)}
              helper="Distinct orders in fct_sales"
            />
            <KpiCard
              label="Order items"
              value={formatInteger(data.total_order_items)}
              helper="Item-grain sales rows"
            />
            <KpiCard
              label="Item revenue"
              value={formatCurrency(data.total_item_revenue)}
              helper="Sum of item_price"
            />
            <KpiCard
              label="Freight value"
              value={formatCurrency(data.total_freight_value)}
              helper="Sum of item-side freight"
            />
            <KpiCard
              label="Gross merchandise value"
              value={formatCurrency(data.total_gross_merchandise_value)}
              helper="Item revenue plus freight"
            />
            <KpiCard
              label="Average order value"
              value={formatCurrency(data.average_order_value_item_side)}
              helper="Item-side revenue per order"
            />
          </>
        )}
      </SectionResource>
    </section>
  );
}

function DailyRevenueSection({
  rows,
  orderStatus,
}: {
  rows: DailyRevenueRow[];
  orderStatus: string;
}) {
  const sortedRows = useMemo(
    () =>
      rows
        .slice()
        .sort((left, right) =>
          left.order_purchase_date.localeCompare(right.order_purchase_date),
        ),
    [rows],
  );
  const totals = useMemo(
    () =>
      rows.reduce(
        (accumulator, row) => ({
          orders: accumulator.orders + row.order_count,
          items: accumulator.items + row.order_item_count,
          gmv: accumulator.gmv + row.gross_merchandise_value,
        }),
        { orders: 0, items: 0, gmv: 0 },
      ),
    [rows],
  );

  return (
    <div>
      <div className="summary-strip">
        <span>
          {formatDate(sortedRows[0]?.order_purchase_date)} to{" "}
          {formatDate(sortedRows[sortedRows.length - 1]?.order_purchase_date)}
        </span>
        <span>Status: {orderStatus ? formatLabel(orderStatus) : "All statuses"}</span>
        <span>{formatInteger(totals.orders)} orders in the displayed window</span>
        <span>{formatCurrency(totals.gmv)} GMV in the displayed window</span>
      </div>
      <DailyRevenueChart rows={sortedRows} />
    </div>
  );
}

function CategorySection({ rows }: { rows: CategoryPerformanceRow[] }) {
  const chartRows: RevenueBarPoint[] = rows
    .slice()
    .reverse()
    .map((row) => ({
      label: formatLabel(row.product_category_name_english ?? row.product_category_name),
      count: row.order_item_count,
      value: row.gross_merchandise_value,
    }));

  return (
    <div className="split-section">
      <RevenueBarChart rows={chartRows} />
      <RankedTable
        rows={rows.map((row) => ({
          label: formatLabel(row.product_category_name_english ?? row.product_category_name),
          countLabel: "Items",
          count: row.order_item_count,
          revenue: row.gross_merchandise_value,
        }))}
      />
    </div>
  );
}

function SellerSection({ rows }: { rows: SellerPerformanceRow[] }) {
  const chartRows: RevenueBarPoint[] = rows
    .slice()
    .reverse()
    .map((row) => ({
      label: row.seller_id.slice(0, 8),
      context: `State: ${row.seller_state ?? "n/a"}`,
      count: row.order_item_count,
      value: row.gross_merchandise_value,
    }));

  return (
    <div className="split-section">
      <RevenueBarChart rows={chartRows} />
      <RankedTable
        rows={rows.map((row) => ({
          label: row.seller_id.slice(0, 12),
          context: row.seller_state ?? "n/a",
          countLabel: "Items",
          count: row.order_item_count,
          revenue: row.gross_merchandise_value,
        }))}
      />
    </div>
  );
}

function CustomerStateSection({ rows }: { rows: CustomerStatePerformanceRow[] }) {
  const chartRows: RevenueBarPoint[] = rows
    .slice()
    .reverse()
    .map((row) => ({
      label: row.customer_state ?? "Unknown",
      count: row.order_count,
      value: row.gross_merchandise_value,
    }));

  return (
    <div className="split-section">
      <RevenueBarChart rows={chartRows} height={280} />
      <RankedTable
        rows={rows.map((row) => ({
          label: row.customer_state ?? "Unknown",
          countLabel: "Orders",
          count: row.order_count,
          revenue: row.gross_merchandise_value,
        }))}
      />
    </div>
  );
}

function OrderStatusSection({ rows }: { rows: OrderStatusSummaryRow[] }) {
  const chartRows: SummaryBarPoint[] = rows.map((row) => ({
    label: formatLabel(row.order_status),
    count: row.order_count,
    value: row.gross_merchandise_value,
    valueLabel: "GMV",
  }));

  return (
    <>
      <SummaryBarChart rows={chartRows} valueColor="#0f766e" />
      <div className="table-wrap table-wrap--compact">
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Orders</th>
              <th>Items</th>
              <th>GMV</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.order_status}>
                <td>{formatLabel(row.order_status)}</td>
                <td className="numeric-cell">{formatInteger(row.order_count)}</td>
                <td className="numeric-cell">{formatInteger(row.order_item_count)}</td>
                <td className="numeric-cell">{formatCurrency(row.gross_merchandise_value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function PaymentTypeSection({ rows }: { rows: PaymentTypeSummaryRow[] }) {
  const chartRows: SummaryBarPoint[] = rows.map((row) => ({
    label: formatLabel(row.payment_type),
    count: row.payment_count,
    value: row.total_payment_value,
    valueLabel: "Payment value",
  }));

  return (
    <>
      <SummaryBarChart rows={chartRows} valueColor="#2563eb" />
      <div className="table-wrap table-wrap--compact">
        <table>
          <thead>
            <tr>
              <th>Payment type</th>
              <th>Payments</th>
              <th>Total value</th>
              <th>Average value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.payment_type}>
                <td>{formatLabel(row.payment_type)}</td>
                <td className="numeric-cell">{formatInteger(row.payment_count)}</td>
                <td className="numeric-cell">{formatCurrency(row.total_payment_value)}</td>
                <td className="numeric-cell">{formatCurrency(row.average_payment_value)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
