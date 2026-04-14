import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { apiClient } from "../api/client";
import { type ResourceState, useApiResource } from "../api/useApiResource";
import { MetricCard } from "../components/MetricCard";
import { SectionState } from "../components/SectionState";
import type {
  AutomationAiSummaryRow,
  DashboardKpis,
  HealthStatus,
  IndustrySummaryRow,
  JobTitleSummaryRow,
  LocationSummaryRow,
} from "../types/api";
import { formatCurrency, formatInteger, formatLabel, formatPercent } from "./formatters";

const rolePalette = ["#0891b2", "#0f766e", "#2563eb", "#14b8a6", "#64748b"];
const industryPalette = ["#06b6d4", "#0f766e", "#2563eb", "#059669", "#64748b"];
const categoryScore: Record<string, number> = { low: 1, medium: 2, high: 3 };

type RoleChartPoint = { name: string; averageSalary: number; recordCount: number };

type IndustryChartPoint = {
  industry: string;
  averageSalary: number;
  remoteShare: number;
  totalRecords: number;
};

type AutomationChartPoint = {
  label: string;
  aiScore: number;
  automationScore: number;
  totalRecords: number;
  averageSalary: number;
  growthShare: number;
};

type LocationChartPoint = {
  location: string;
  averageSalary: number;
  remoteShare: number;
};

export function Dashboard() {
  const health = useApiResource<HealthStatus>(apiClient.getHealth);

  return (
    <div className="dashboard-shell">
      <Sidebar health={health} />
      <main className="dashboard-main">
        <Header health={health} />
        <div className="dashboard-content">
          <KpiSection />
          <HeroSection />
          <SecondaryChartGrid />
          <IndustryDeepDiveSection />
        </div>
      </main>
    </div>
  );
}

function Sidebar({ health }: { health: ResourceState<HealthStatus> }) {
  const isConnected = health.data?.status === "ok" && !health.error;
  const statusLabel = health.isLoading ? "Checking" : isConnected ? "Connected" : "Offline";
  const navItems = [
    ["Dashboard", "DB"],
    ["Market Trends", "MT"],
    ["Salary Insights", "$"],
    ["Role Analysis", "RA"],
    ["DBT Lineage", "DL"],
    ["Data Quality", "DQ"],
  ];
  const pipelineItems = [
    ["Bronze", "Ready"],
    ["Silver", "Ready"],
    ["Gold", "Ready"],
    ["DBT DuckDB", "Validated"],
    ["DBT PostgreSQL", "Validated"],
  ];

  return (
    <aside className="sidebar" aria-label="Dashboard navigation">
      <div className="sidebar__brand">
        <div className="sidebar__logo" aria-hidden="true">JM</div>
        <div>
          <strong>Job Market Analytics</strong>
          <span>Gold + DBT modeling</span>
        </div>
      </div>
      <nav className="sidebar__nav" aria-label="Dashboard sections">
        {navItems.map(([label, icon], index) => (
          <button
            className={`sidebar__nav-item${index === 0 ? " sidebar__nav-item--active" : ""}`}
            type="button"
            key={label}
          >
            <span aria-hidden="true">{icon}</span>
            {label}
          </button>
        ))}
      </nav>
      <section className="sidebar-panel" aria-labelledby="pipeline-status-heading">
        <div className="sidebar-panel__heading" id="pipeline-status-heading">
          Pipeline Status
        </div>
        <div className="pipeline-stack">
          {pipelineItems.map(([label, value]) => (
            <div className="pipeline-badge" key={label}>
              <div>
                <span>{label}</span>
                <strong>{value}</strong>
              </div>
              <i aria-hidden="true" />
            </div>
          ))}
        </div>
      </section>
      <section className="sidebar-panel" aria-labelledby="read-path-heading">
        <div className="sidebar-panel__heading" id="read-path-heading">Read Path</div>
        <dl className="system-list">
          <div>
            <dt>PostgreSQL</dt>
            <dd>marts schema</dd>
          </div>
          <div>
            <dt>Flask API</dt>
            <dd className={isConnected ? "is-online" : "is-offline"}>{statusLabel}</dd>
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
  const statusLabel = health.isLoading ? "Checking API" : isConnected ? "PostgreSQL Path Active" : "API Offline";

  return (
    <header className="dashboard-header">
      <div>
        <h1>Job Market Intelligence</h1>
        <p>Curated labor-market analytics from medallion processing and DBT marts.</p>
      </div>
      <div className={`connection-badge connection-badge--${statusTone}`}>
        <span aria-hidden="true" />
        <strong>{statusLabel}</strong>
        <small>{health.error ? health.error : health.data?.source ?? "marts + Silver"}</small>
      </div>
    </header>
  );
}

function SectionHeading({
  id,
  title,
  description,
  source,
}: {
  id: string;
  title: string;
  description: string;
  source: string;
}) {
  return (
    <div className="section-heading">
      <div>
        <h2 id={id}>{title}</h2>
        <p>{description}</p>
      </div>
      <span className="source-pill">{source}</span>
    </div>
  );
}

function KpiSection() {
  const { data, error, isLoading } = useApiResource<DashboardKpis>(apiClient.getKpis);

  return (
    <section className="metric-grid" aria-label="Dashboard KPIs">
      {isLoading ? (
        <SectionState message="Loading dashboard KPIs..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : !data ? (
        <SectionState message="No KPI data returned by the API." tone="empty" />
      ) : (
        <>
          <MetricCard label="Total Records" value={formatInteger(data.total_records)} helper="Modeled Silver rows" source="analytics.job_market_insights_silver" tone="cyan" />
          <MetricCard label="Average Salary" value={formatCurrency(data.average_salary_usd)} helper="Mean salary across records" source="Silver KPI query" tone="blue" />
          <MetricCard label="Median Salary" value={formatCurrency(data.median_salary_usd)} helper="Dataset median salary" source="Silver KPI query" tone="green" />
          <MetricCard label="Remote-Friendly" value={formatPercent(data.remote_friendly_share)} helper="Share flagged remote" source="Silver KPI query" tone="cyan" />
          <MetricCard label="High AI Adoption" value={formatPercent(data.high_ai_adoption_share)} helper="Share marked high" source="Silver KPI query" tone="green" />
          <MetricCard label="High Automation Risk" value={formatPercent(data.high_automation_risk_share)} helper="Share marked high" source="Silver KPI query" tone="amber" />
        </>
      )}
    </section>
  );
}

function HeroSection() {
  const { data, error, isLoading } = useApiResource<IndustrySummaryRow[]>(
    apiClient.getIndustrySummary,
  );
  const chartData: IndustryChartPoint[] =
    data
      ?.slice()
      .sort((left, right) => (right.average_salary_usd ?? 0) - (left.average_salary_usd ?? 0))
      .slice(0, 8)
      .map((row) => ({
        industry: formatLabel(row.industry),
        averageSalary: row.average_salary_usd ?? 0,
        remoteShare: (row.remote_friendly_share ?? 0) * 100,
        totalRecords: row.total_records ?? 0,
      })) ?? [];

  return (
    <section className="section-block section-block--hero" aria-labelledby="hero-heading">
      <SectionHeading
        id="hero-heading"
        title="Industry Salary and Remote Mix"
        description="A real mart-backed comparison of average salary and remote-friendly share by industry."
        source="marts.mart_industry_summary"
      />
      {isLoading ? (
        <SectionState message="Loading industry summary..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : chartData.length === 0 ? (
        <SectionState message="No industry rows returned by the API." tone="empty" />
      ) : (
        <div className="chart-frame chart-frame--hero">
          <ResponsiveContainer width="100%" height={360}>
            <ComposedChart data={chartData} margin={{ top: 16, right: 28, bottom: 8, left: 8 }}>
              <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 8" />
              <XAxis dataKey="industry" tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 11 }} tickMargin={14} />
              <YAxis yAxisId="salary" tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(value: number) => formatCurrency(value)} width={76} />
              <YAxis yAxisId="share" orientation="right" domain={[0, 100]} tickLine={false} axisLine={false} tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(value: number) => `${value}%`} width={48} />
              <Tooltip content={<HeroTooltip />} cursor={{ fill: "#f8fafc" }} />
              <Bar yAxisId="salary" dataKey="averageSalary" name="Average salary" radius={[6, 6, 0, 0]} maxBarSize={44}>
                {chartData.map((row, index) => (
                  <Cell fill={industryPalette[index % industryPalette.length]} key={row.industry} />
                ))}
              </Bar>
              <Line yAxisId="share" type="monotone" dataKey="remoteShare" name="Remote-friendly share" stroke="#111827" strokeWidth={2} dot={{ r: 4, fill: "#111827", stroke: "#ffffff", strokeWidth: 2 }} />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
      )}
    </section>
  );
}

function HeroTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: IndustryChartPoint }>;
}) {
  if (!active || !payload?.[0]) {
    return null;
  }

  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.industry}</strong>
      <span>Avg salary: {formatCurrency(row.averageSalary)}</span>
      <span>Remote-friendly: {row.remoteShare.toFixed(1)}%</span>
      <span>Records: {formatInteger(row.totalRecords)}</span>
    </div>
  );
}

function SecondaryChartGrid() {
  return (
    <section className="chart-grid" aria-label="Secondary mart charts">
      <RoleSalarySection />
      <AutomationRiskSection />
      <LocationRankingSection />
    </section>
  );
}

function RoleSalarySection() {
  const { data, error, isLoading } = useApiResource<JobTitleSummaryRow[]>(
    apiClient.getJobTitleSummary,
  );
  const rows: RoleChartPoint[] =
    data
      ?.map((row) => ({
        name: formatLabel(row.job_title),
        averageSalary: row.average_salary_usd ?? 0,
        recordCount: row.total_records ?? 0,
      }))
      .sort((left, right) => left.averageSalary - right.averageSalary) ?? [];

  return (
    <section className="section-block" aria-labelledby="role-salary-heading">
      <SectionHeading id="role-salary-heading" title="Top Roles by Salary" description="Highest average salaries by modeled job title." source="marts.mart_job_title_summary" />
      {isLoading ? (
        <SectionState message="Loading role summary..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No role rows returned." tone="empty" />
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={rows} layout="vertical" margin={{ top: 8, right: 12, bottom: 4, left: 24 }} barCategoryGap={14}>
            <CartesianGrid stroke="#edf2f7" strokeDasharray="4 8" horizontal={false} />
            <XAxis type="number" tickLine={false} axisLine={false} tickFormatter={(value: number) => formatCurrency(value)} />
            <YAxis dataKey="name" type="category" width={122} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#64748b" }} />
            <Tooltip content={<RoleTooltip />} cursor={{ fill: "#f8fafc" }} />
            <Bar dataKey="averageSalary" radius={[0, 6, 6, 0]} maxBarSize={22}>
              {rows.map((row, index) => (
                <Cell fill={rolePalette[index % rolePalette.length]} key={row.name} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}

function RoleTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: RoleChartPoint }>;
}) {
  if (!active || !payload?.[0]) {
    return null;
  }
  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.name}</strong>
      <span>Avg salary: {formatCurrency(row.averageSalary)}</span>
      <span>Records: {formatInteger(row.recordCount)}</span>
    </div>
  );
}

function AutomationRiskSection() {
  const { data, error, isLoading } = useApiResource<AutomationAiSummaryRow[]>(
    apiClient.getAutomationAiSummary,
  );
  const rows: AutomationChartPoint[] =
    data?.map((row) => {
      const aiLabel = formatLabel(row.ai_adoption_level);
      const riskLabel = formatLabel(row.automation_risk);
      return {
        label: `${aiLabel} AI / ${riskLabel} Risk`,
        aiScore: categoryScore[row.ai_adoption_level] ?? 0,
        automationScore: categoryScore[row.automation_risk] ?? 0,
        totalRecords: row.total_records ?? 0,
        averageSalary: row.average_salary_usd ?? 0,
        growthShare: row.growth_projection_share ?? 0,
      };
    }) ?? [];

  return (
    <section className="section-block" aria-labelledby="automation-heading">
      <SectionHeading id="automation-heading" title="AI Adoption vs Automation Risk" description="Risk and adoption groups from the automation and AI mart." source="marts.mart_automation_ai_summary" />
      {isLoading ? (
        <SectionState message="Loading automation and AI summary..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No automation rows returned." tone="empty" />
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <ScatterChart margin={{ top: 20, right: 24, bottom: 18, left: 12 }}>
            <CartesianGrid stroke="#e2e8f0" strokeDasharray="4 8" />
            <XAxis type="number" dataKey="aiScore" name="AI adoption" domain={[0.5, 3.5]} ticks={[1, 2, 3]} tickLine={false} axisLine={false} tickFormatter={(value: number) => ["", "Low", "Medium", "High"][value] ?? ""} />
            <YAxis type="number" dataKey="automationScore" name="Automation risk" domain={[0.5, 3.5]} ticks={[1, 2, 3]} tickLine={false} axisLine={false} tickFormatter={(value: number) => ["", "Low", "Medium", "High"][value] ?? ""} />
            <Tooltip content={<AutomationTooltip />} cursor={{ strokeDasharray: "4 6" }} />
            <Scatter data={rows} fill="#0f766e" />
          </ScatterChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}

function AutomationTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: AutomationChartPoint }>;
}) {
  if (!active || !payload?.[0]) {
    return null;
  }
  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.label}</strong>
      <span>Records: {formatInteger(row.totalRecords)}</span>
      <span>Avg salary: {formatCurrency(row.averageSalary)}</span>
      <span>Growth share: {formatPercent(row.growthShare)}</span>
    </div>
  );
}

function LocationRankingSection() {
  const { data, error, isLoading } = useApiResource<LocationSummaryRow[]>(
    apiClient.getLocationSummary,
  );
  const rows: LocationChartPoint[] =
    data
      ?.map((row) => ({
        location: formatLabel(row.location),
        averageSalary: row.average_salary_usd ?? 0,
        remoteShare: row.remote_friendly_share ?? 0,
      }))
      .sort((left, right) => left.averageSalary - right.averageSalary) ?? [];

  return (
    <section className="section-block" aria-labelledby="location-heading">
      <SectionHeading id="location-heading" title="Location Salary Ranking" description="Top locations by average salary from the location mart." source="marts.mart_location_summary" />
      {isLoading ? (
        <SectionState message="Loading location summary..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No location rows returned." tone="empty" />
      ) : (
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={rows} layout="vertical" margin={{ top: 8, right: 12, bottom: 4, left: 24 }}>
            <CartesianGrid stroke="#edf2f7" strokeDasharray="4 8" horizontal={false} />
            <XAxis type="number" tickLine={false} axisLine={false} tickFormatter={(value: number) => formatCurrency(value)} />
            <YAxis dataKey="location" type="category" width={122} tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "#64748b" }} />
            <Tooltip content={<LocationTooltip />} cursor={{ fill: "#f8fafc" }} />
            <Bar dataKey="averageSalary" fill="#0891b2" radius={[0, 6, 6, 0]} maxBarSize={22} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </section>
  );
}

function LocationTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: Array<{ payload: LocationChartPoint }>;
}) {
  if (!active || !payload?.[0]) {
    return null;
  }
  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.location}</strong>
      <span>Avg salary: {formatCurrency(row.averageSalary)}</span>
      <span>Remote-friendly: {formatPercent(row.remoteShare)}</span>
    </div>
  );
}

function IndustryDeepDiveSection() {
  const { data, error, isLoading } = useApiResource<IndustrySummaryRow[]>(
    apiClient.getIndustrySummary,
  );
  const rows =
    data
      ?.slice()
      .sort((left, right) => (right.total_records ?? 0) - (left.total_records ?? 0)) ??
    [];

  return (
    <section className="section-block section-block--table" aria-labelledby="industry-heading">
      <SectionHeading id="industry-heading" title="Industry Deep Dive" description="Comprehensive analytics by industry sector with salary, remote, AI, automation, and growth signals." source="marts.mart_industry_summary" />
      {isLoading ? (
        <SectionState message="Loading industry deep dive..." />
      ) : error ? (
        <SectionState message={error} tone="error" />
      ) : rows.length === 0 ? (
        <SectionState message="No industry rows returned." tone="empty" />
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Industry</th>
                <th>Records</th>
                <th>Avg Salary</th>
                <th>Median Salary</th>
                <th>Remote</th>
                <th>High AI</th>
                <th>Automation Risk</th>
                <th>Growth</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.industry}>
                  <td><span className="industry-name">{formatLabel(row.industry)}</span></td>
                  <td className="numeric-cell">{formatInteger(row.total_records)}</td>
                  <td className="numeric-cell">{formatCurrency(row.average_salary_usd)}</td>
                  <td className="numeric-cell">{formatCurrency(row.median_salary_usd)}</td>
                  <td><ShareMeter value={row.remote_friendly_share} /></td>
                  <td><RiskPill value={row.high_ai_adoption_share} positive /></td>
                  <td><RiskPill value={row.high_automation_risk_share} /></td>
                  <td className="numeric-cell">{formatPercent(row.growth_projection_share)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function ShareMeter({ value }: { value: number | null }) {
  const percent = Math.max(0, Math.min(100, (value ?? 0) * 100));
  return (
    <div className="share-meter" aria-label={`Remote-friendly share ${percent.toFixed(1)}%`}>
      <span><i style={{ width: `${percent}%` }} /></span>
      <strong>{formatPercent(value)}</strong>
    </div>
  );
}

function RiskPill({
  value,
  positive = false,
}: {
  value: number | null;
  positive?: boolean;
}) {
  const numeric = value ?? 0;
  const level = numeric >= 0.66 ? "high" : numeric >= 0.33 ? "medium" : "low";
  return (
    <span className={`risk-pill risk-pill--${level}${positive ? " risk-pill--positive" : ""}`}>
      {formatPercent(value)}
    </span>
  );
}
