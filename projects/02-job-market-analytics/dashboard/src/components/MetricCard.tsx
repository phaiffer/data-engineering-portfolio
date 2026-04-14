type MetricCardProps = {
  label: string;
  value: string;
  helper: string;
  source: string;
  tone?: "blue" | "cyan" | "green" | "amber" | "violet";
};

export function MetricCard({
  label,
  value,
  helper,
  source,
  tone = "blue",
}: MetricCardProps) {
  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__topline">
        <span>{label}</span>
        <i aria-hidden="true" />
      </div>
      <strong>{value}</strong>
      <small>{helper}</small>
      <div className="metric-card__source">{source}</div>
    </article>
  );
}
