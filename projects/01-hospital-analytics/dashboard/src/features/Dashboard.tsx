import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { apiClient } from "../api/client";
import { useApiResource } from "../api/useApiResource";
import { MetricCard } from "../components/MetricCard";
import { SectionState } from "../components/SectionState";
import type {
  DailyPatientFlowRow,
  DashboardKpis,
  DemographicSummaryRow,
  DepartmentReferralRow,
  HealthStatus,
} from "../types/api";
import {
  formatDateLabel,
  formatDecimal,
  formatInteger,
  formatNullableLabel,
  formatPercent,
} from "./formatters";

type ResourceState<T> = {
  data: T | null;
  error: string | null;
  isLoading: boolean;
};

const referralPalette = ["#1e3a8a", "#059669", "#06b6d4", "#94a3b8", "#cbd5e1"];
const visibleReferralGroups = 7;
const visibleDailyFlowPoints = 7;

type DailyPatientFlowChartPoint = {
  date: string;
  events: number;
  waitTime: number;
};

function toSortableDateValue(value: string | null): number {
  if (!value) {
    return Number.NEGATIVE_INFINITY;
  }

  const timestamp = new Date(`${value}T00:00:00`).getTime();
  return Number.isNaN(timestamp) ? Number.NEGATIVE_INFINITY : timestamp;
}

function toDailyFlowPresentationData(
  rows: DailyPatientFlowRow[] | null,
): DailyPatientFlowChartPoint[] {
  return (
    rows
      ?.slice()
      .sort((left, right) => {
        return (
          toSortableDateValue(left.admission_date) -
          toSortableDateValue(right.admission_date)
        );
      })
      .slice(-visibleDailyFlowPoints)
      .map((row) => ({
        date: formatDateLabel(row.admission_date),
        events: row.total_patient_events ?? 0,
        waitTime: row.average_patient_waittime ?? 0,
      })) ?? []
  );
}

export function Dashboard() {
  const health = useApiResource<HealthStatus>(apiClient.getHealth);

  return (
    <div className="dashboard-product-shell">
      <Sidebar health={health} />
      <main className="dashboard-main">
        <Header health={health} />
        <div className="dashboard-content">
          <KpiSection />
          <section className="dashboard-grid" aria-label="Patient flow analytics">
            <DailyPatientFlowSection />
            <DepartmentReferralSection />
          </section>
          <DemographicsSection />
        </div>
      </main>
    </div>
  );
}

function Sidebar({ health }: { health: ResourceState<HealthStatus> }) {
  const navItems = ["Dashboard", "Data Lineage", "API Logs", "Monitoring"];
  const apiConnected = health.data?.status === "ok" && !health.error;

  return (
    <aside className="sidebar" aria-label="Dashboard navigation">
      <div className="sidebar__brand">
        <div className="sidebar__logo" aria-hidden="true">
          HA
        </div>
        <div>
          <strong>Hospital Analytics</strong>
          <span>Gold Layer serving</span>
        </div>
      </div>

      <nav className="sidebar__nav" aria-label="Dashboard sections">
        {navItems.map((item, index) => (
          <button
            className={`sidebar__nav-item${
              index === 0 ? " sidebar__nav-item--active" : ""
            }`}
            type="button"
            key={item}
          >
            <span aria-hidden="true">{item.slice(0, 2)}</span>
            {item}
          </button>
        ))}
      </nav>

      <section className="sidebar-panel" aria-labelledby="pipeline-status-heading">
        <div className="sidebar-panel__heading" id="pipeline-status-heading">
          Pipeline status
        </div>
        <div className="pipeline-stack">
          {["Bronze", "Silver", "Gold"].map((layer) => (
            <div className="pipeline-badge" key={layer}>
              <span>{layer}</span>
              <strong>Ready</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="sidebar-panel" aria-labelledby="system-health-heading">
        <div className="sidebar-panel__heading" id="system-health-heading">
          System health
        </div>
        <dl className="system-health-list">
          <div>
            <dt>PostgreSQL</dt>
            <dd className="is-neutral">Via API</dd>
          </div>
          <div>
            <dt>Flask API</dt>
            <dd className={apiConnected ? "is-online" : "is-offline"}>
              {health.isLoading ? "Checking" : apiConnected ? "Connected" : "Offline"}
            </dd>
          </div>
          <div>
            <dt>Base URL</dt>
            <dd title={apiClient.baseUrl}>{apiClient.baseUrl}</dd>
          </div>
        </dl>
      </section>
    </aside>
  );
}

function Header({ health }: { health: ResourceState<HealthStatus> }) {
  const isConnected = health.data?.status === "ok" && !health.error;
  const statusTone = health.isLoading ? "checking" : isConnected ? "online" : "offline";
  const statusLabel = health.isLoading
    ? "Checking"
    : isConnected
      ? `API Connected: ${health.data?.service ?? "hospital-analytics-api"}`
      : "API Unavailable";

  return (
    <header className="dashboard-header">
      <div>
        <span className="eyebrow">Curated Gold Layer Outputs</span>
        <h1>Hospital Patient Flow Intelligence</h1>
        <p>
          Operational metrics served by Flask from PostgreSQL views, prepared for
          portfolio demos and analytics review.
        </p>
      </div>
      <div className={`connection-badge connection-badge--${statusTone}`}>
        <span aria-hidden="true" />
        <strong>{statusLabel}</strong>
        {health.error ? <small>{health.error}</small> : null}
      </div>
    </header>
  );
}

function SectionHeading({
  id,
  eyebrow,
  title,
  description,
  source,
}: {
  id: string;
  eyebrow: string;
  title: string;
  description: string;
  source?: string;
}) {
  return (
    <div className="section-heading">
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h2 id={id}>{title}</h2>
        <p>{description}</p>
      </div>
      {source ? <span className="source-pill">{source}</span> : null}
    </div>
  );
}

function KpiSection() {
  const { data, error, isLoading } = useApiResource<DashboardKpis>(
    apiClient.getKpis,
  );

  return (
    <section className="section-block" aria-labelledby="kpi-heading">
      <SectionHeading
        id="kpi-heading"
        eyebrow="Serving view"
        title="Portfolio KPIs"
        description="Single-row metrics from the dashboard KPI endpoint."
        source="/api/v1/kpis"
      />

      {isLoading ? (
        <SectionState message="Loading KPI metrics..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : !data || Object.keys(data).length === 0 ? (
        <SectionState message="No KPI data returned by the API." tone="empty" />
      ) : (
        <div className="metric-grid">
          <MetricCard
            label="Total events"
            value={formatInteger(data.total_patient_events)}
            helper="All patient events in the serving layer"
            source="v_dashboard_kpis"
            tone="blue"
            emphasis
          />
          <MetricCard
            label="Avg wait time"
            value={formatDecimal(data.average_waittime_overall)}
            unit="min"
            helper="Mean wait time per event"
            source="v_dashboard_kpis"
            tone="amber"
          />
          <MetricCard
            label="Satisfaction"
            value={formatDecimal(data.average_satisfaction_overall)}
            helper="Average patient score"
            source="v_dashboard_kpis"
            tone="green"
          />
          <MetricCard
            label="Daily points"
            value={formatInteger(data.number_of_daily_points)}
            helper="Admission dates"
            source="daily flow"
            tone="cyan"
          />
          <MetricCard
            label="Departments"
            value={formatInteger(data.number_of_department_groups)}
            helper="Referral categories"
            source="department referrals"
            tone="green"
          />
          <MetricCard
            label="Demographics"
            value={formatInteger(data.number_of_demographic_groups)}
            helper="Gender, race, and age bands"
            source="demographics"
            tone="blue"
          />
        </div>
      )}
    </section>
  );
}

function DailyPatientFlowSection() {
  const { data, error, isLoading } = useApiResource<DailyPatientFlowRow[]>(
    apiClient.getDailyPatientFlow,
  );

  const chartData = toDailyFlowPresentationData(data);

  return (
    <section
      className="section-block section-block--primary-chart"
      aria-labelledby="daily-flow-heading"
    >
      <SectionHeading
        id="daily-flow-heading"
        eyebrow="Daily trend"
        title="Daily patient flow trends"
        description="Patient events are the primary signal; average wait time is shown as supporting context."
        source="/api/v1/daily-patient-flow"
      />

      {isLoading ? (
        <SectionState message="Loading daily patient flow..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : chartData.length === 0 ? (
        <SectionState message="No daily patient flow rows returned." tone="empty" />
      ) : (
        <div
          className="chart-frame chart-frame--flow"
          role="img"
          aria-label="Daily patient flow chart"
        >
          <div className="chart-legend" aria-hidden="true">
            <span className="chart-legend__item chart-legend__item--events">
              Patient events
            </span>
            <span className="chart-legend__item chart-legend__item--wait">
              Avg wait time
            </span>
          </div>
          <ResponsiveContainer width="100%" height={330}>
            <ComposedChart
              data={chartData}
              margin={{ top: 26, right: 10, left: -2, bottom: 0 }}
            >
              <defs>
                <linearGradient id="eventsGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="8%" stopColor="#1e3a8a" stopOpacity={0.22} />
                  <stop offset="92%" stopColor="#1e3a8a" stopOpacity={0.04} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#e8edf5" strokeDasharray="3 6" />
              <XAxis
                dataKey="date"
                interval="preserveStartEnd"
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#64748b", fontSize: 11 }}
                tickMargin={12}
              />
              <YAxis
                yAxisId="events"
                width={48}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#64748b", fontSize: 11 }}
                tickCount={5}
                tickFormatter={(value: number) => formatInteger(value)}
              />
              <YAxis
                yAxisId="waitTime"
                orientation="right"
                width={44}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "#64748b", fontSize: 11 }}
                tickCount={5}
                tickFormatter={(value: number) => formatDecimal(value)}
              />
              <Tooltip
                cursor={{ stroke: "#94a3b8", strokeDasharray: "3 5" }}
                contentStyle={{
                  border: "1px solid #e2e8f0",
                  borderRadius: 8,
                  boxShadow: "0 14px 34px rgb(15 23 42 / 12%)",
                  fontFamily: "var(--font-technical)",
                  padding: "10px 12px",
                }}
                labelStyle={{ color: "#0f172a", marginBottom: 6 }}
                itemStyle={{ color: "#475569" }}
                formatter={(value, name) => [
                  name === "Avg wait time"
                    ? `${formatDecimal(Number(value))} min`
                    : formatInteger(Number(value)),
                  name,
                ]}
              />
              <Area
                yAxisId="events"
                type="monotone"
                dataKey="events"
                name="Patient events"
                stroke="#1e3a8a"
                strokeWidth={2}
                fill="url(#eventsGradient)"
                dot={false}
                activeDot={{ r: 5, stroke: "#ffffff", strokeWidth: 2 }}
              />
              <Line
                yAxisId="waitTime"
                type="monotone"
                dataKey="waitTime"
                name="Avg wait time"
                stroke="#f59e0b"
                strokeWidth={2.25}
                dot={false}
                activeDot={{ r: 4, stroke: "#ffffff", strokeWidth: 2 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

function DepartmentReferralSection() {
  const { data, error, isLoading } = useApiResource<DepartmentReferralRow[]>(
    apiClient.getDepartmentReferrals,
  );

  const rows =
    data
      ?.map((row) => ({
        ...row,
        departmentLabel: formatNullableLabel(row.department_referral),
        total_patient_events: row.total_patient_events ?? 0,
      }))
      .sort((left, right) => right.total_patient_events - left.total_patient_events) ??
    [];
  const chartRows = rows.slice(0, visibleReferralGroups);

  return (
    <section className="section-block" aria-labelledby="department-heading">
      <SectionHeading
        id="department-heading"
        eyebrow="Referral mix"
        title="Referral distribution"
        description="Event volume and share of total events by department group."
        source="/api/v1/department-referrals"
      />

      {isLoading ? (
        <SectionState message="Loading department referrals..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No department referral rows returned." tone="empty" />
      ) : (
        <>
          {rows.length > visibleReferralGroups ? (
            <p className="chart-note">
              Showing top {visibleReferralGroups} referral groups in the chart; full
              detail remains in the table.
            </p>
          ) : null}
          <div
            className="chart-frame chart-frame--referrals"
            role="img"
            aria-label="Department referral horizontal bar chart"
          >
            <ResponsiveContainer width="100%" height={290}>
              <BarChart
                data={chartRows}
                layout="vertical"
                margin={{ top: 6, right: 12, left: 8, bottom: 0 }}
                barCategoryGap={14}
              >
                <CartesianGrid stroke="#eef2f7" strokeDasharray="4 8" horizontal={false} />
                <XAxis
                  type="number"
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value: number) => formatInteger(value)}
                />
                <YAxis
                  dataKey="departmentLabel"
                  type="category"
                  width={136}
                  tickLine={false}
                  axisLine={false}
                  tick={{ fontSize: 11, width: 130 }}
                />
                <Tooltip
                  cursor={{ fill: "#f8fafc" }}
                  contentStyle={{
                    border: "1px solid #e2e8f0",
                    borderRadius: 8,
                    boxShadow: "0 14px 34px rgb(15 23 42 / 12%)",
                    fontFamily: "var(--font-technical)",
                  }}
                  formatter={(value) => [formatInteger(Number(value)), "Patient events"]}
                />
                <Bar
                  dataKey="total_patient_events"
                  name="Patient events"
                  radius={[0, 4, 4, 0]}
                  maxBarSize={24}
                >
                  {chartRows.map((row, index) => (
                    <Cell
                      fill={referralPalette[index % referralPalette.length]}
                      opacity={index === 0 ? 1 : 0.82}
                      key={`${row.departmentLabel}-${index}`}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="table-wrap table-wrap--compact">
            <table>
              <thead>
                <tr>
                  <th>Department referral</th>
                  <th>Events</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${row.departmentLabel}-${index}`}>
                    <td>{row.departmentLabel}</td>
                    <td className="numeric-cell">
                      {formatInteger(row.total_patient_events)}
                    </td>
                    <td className="numeric-cell">
                      {formatPercent(row.share_of_total_events)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
}

function DemographicsSection() {
  const { data, error, isLoading } = useApiResource<DemographicSummaryRow[]>(
    apiClient.getDemographics,
  );

  const rows =
    data
      ?.map((row) => ({
        ...row,
        total_patient_events: row.total_patient_events ?? 0,
      }))
      .sort((left, right) => right.total_patient_events - left.total_patient_events) ??
    [];

  return (
    <section className="section-block section-block--table" aria-labelledby="demographics-heading">
      <SectionHeading
        id="demographics-heading"
        eyebrow="Population view"
        title="Demographics deep-dive"
        description="Grouped operational metrics by gender, race, and age band."
        source="/api/v1/demographics"
      />

      {isLoading ? (
        <SectionState message="Loading demographic summary..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No demographic rows returned." tone="empty" />
      ) : (
        <div className="table-wrap table-wrap--large">
          <table>
            <thead>
              <tr>
                <th>Gender</th>
                <th>Race</th>
                <th>Age band</th>
                <th>Events</th>
                <th>Avg wait</th>
                <th>Avg satisfaction</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => (
                <tr
                  key={`${row.patient_gender}-${row.patient_race}-${row.patient_age_band}-${index}`}
                >
                  <td>{formatNullableLabel(row.patient_gender)}</td>
                  <td>{formatNullableLabel(row.patient_race)}</td>
                  <td>
                    <span className="age-band-pill">
                      {formatNullableLabel(row.patient_age_band)}
                    </span>
                  </td>
                  <td className="numeric-cell">
                    {formatInteger(row.total_patient_events)}
                  </td>
                  <td className="numeric-cell">
                    {formatDecimal(row.average_patient_waittime)}
                  </td>
                  <td className="numeric-cell">
                    {formatDecimal(row.average_patient_satisfaction_score)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
