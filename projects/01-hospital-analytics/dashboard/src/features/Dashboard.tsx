import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
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

export function Dashboard() {
  return (
    <main className="dashboard-shell">
      <header className="dashboard-header">
        <div>
          <span className="eyebrow">Hospital analytics</span>
          <h1>Patient flow serving dashboard</h1>
          <p>
            Curated Gold outputs loaded into PostgreSQL, served through Flask, and
            visualized as an operational analytics dashboard.
          </p>
        </div>
        <HealthStatusCard />
      </header>

      <KpiSection />

      <section className="dashboard-grid">
        <DailyPatientFlowSection />
        <DepartmentReferralSection />
      </section>

      <DemographicsSection />
    </main>
  );
}

function HealthStatusCard() {
  const { data, error, isLoading } = useApiResource<HealthStatus>(
    apiClient.getHealth,
  );

  const statusLabel = data?.status === "ok" ? "Connected" : "Unavailable";

  return (
    <aside className="connection-panel" aria-label="API connection status">
      <span>API status</span>
      {isLoading ? (
        <strong>Checking...</strong>
      ) : error ? (
        <>
          <strong>Unavailable</strong>
          <small>{error}</small>
        </>
      ) : (
        <>
          <strong>{statusLabel}</strong>
          <small>{data?.service ?? "hospital-analytics-api"}</small>
          <small>{apiClient.baseUrl}</small>
        </>
      )}
    </aside>
  );
}

function KpiSection() {
  const { data, error, isLoading } = useApiResource<DashboardKpis>(
    apiClient.getKpis,
  );

  return (
    <section className="section-block" aria-labelledby="kpi-heading">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Serving view</span>
          <h2 id="kpi-heading">Portfolio KPIs</h2>
        </div>
        <p>Single-row metrics from `v_dashboard_kpis`.</p>
      </div>

      {isLoading ? (
        <SectionState message="Loading KPI metrics..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : !data || Object.keys(data).length === 0 ? (
        <SectionState message="No KPI data returned by the API." tone="empty" />
      ) : (
        <div className="metric-grid">
          <MetricCard
            label="Total patient events"
            value={formatInteger(data.total_patient_events)}
            helper="All events in the curated serving layer"
          />
          <MetricCard
            label="Average wait time"
            value={formatDecimal(data.average_waittime_overall)}
            helper="Minutes"
          />
          <MetricCard
            label="Average satisfaction"
            value={formatDecimal(data.average_satisfaction_overall)}
            helper="Score"
          />
          <MetricCard
            label="Daily points"
            value={formatInteger(data.number_of_daily_points)}
            helper="Admission dates"
          />
          <MetricCard
            label="Department groups"
            value={formatInteger(data.number_of_department_groups)}
            helper="Referral categories"
          />
          <MetricCard
            label="Demographic groups"
            value={formatInteger(data.number_of_demographic_groups)}
            helper="Gender, race, and age bands"
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

  const chartData =
    data?.map((row) => ({
      date: formatDateLabel(row.admission_date),
      events: row.total_patient_events ?? 0,
      waitTime: row.average_patient_waittime ?? 0,
    })) ?? [];

  return (
    <section className="section-block" aria-labelledby="daily-flow-heading">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Daily trend</span>
          <h2 id="daily-flow-heading">Patient flow</h2>
        </div>
        <p>Events and wait-time trend by admission date.</p>
      </div>

      {isLoading ? (
        <SectionState message="Loading daily patient flow..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : chartData.length === 0 ? (
        <SectionState message="No daily patient flow rows returned." tone="empty" />
      ) : (
        <div className="chart-frame" role="img" aria-label="Daily patient flow chart">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData} margin={{ top: 12, right: 20, left: 0, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="date" minTickGap={28} />
              <YAxis yAxisId="events" width={44} />
              <YAxis yAxisId="waitTime" orientation="right" width={48} />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="events"
                type="monotone"
                dataKey="events"
                name="Patient events"
                stroke="#0f766e"
                strokeWidth={3}
                dot={false}
              />
              <Line
                yAxisId="waitTime"
                type="monotone"
                dataKey="waitTime"
                name="Avg wait time"
                stroke="#b45309"
                strokeWidth={3}
                dot={false}
              />
            </LineChart>
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

  return (
    <section className="section-block" aria-labelledby="department-heading">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Referral mix</span>
          <h2 id="department-heading">Department referrals</h2>
        </div>
        <p>Event volume and share of total events by referral group.</p>
      </div>

      {isLoading ? (
        <SectionState message="Loading department referrals..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No department referral rows returned." tone="empty" />
      ) : (
        <>
          <div className="chart-frame" role="img" aria-label="Department referral bar chart">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={rows.slice(0, 10)} margin={{ top: 12, right: 16, left: 0, bottom: 8 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="departmentLabel" tick={{ fontSize: 11 }} interval={0} />
                <YAxis width={44} />
                <Tooltip />
                <Bar dataKey="total_patient_events" name="Patient events" fill="#0f766e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Department referral</th>
                  <th>Events</th>
                  <th>Share</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.departmentLabel}>
                    <td>{row.departmentLabel}</td>
                    <td>{formatInteger(row.total_patient_events)}</td>
                    <td>{formatPercent(row.share_of_total_events)}</td>
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
    <section className="section-block" aria-labelledby="demographics-heading">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Population view</span>
          <h2 id="demographics-heading">Demographic summary</h2>
        </div>
        <p>Grouped operational metrics by gender, race, and age band.</p>
      </div>

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
                  <td>{formatNullableLabel(row.patient_age_band)}</td>
                  <td>{formatInteger(row.total_patient_events)}</td>
                  <td>{formatDecimal(row.average_patient_waittime)}</td>
                  <td>{formatDecimal(row.average_patient_satisfaction_score)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

