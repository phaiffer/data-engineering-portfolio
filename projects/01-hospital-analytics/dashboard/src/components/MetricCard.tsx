interface MetricCardProps {
  label: string;
  value: string;
  helper?: string;
  source?: string;
  unit?: string;
  tone?: "blue" | "green" | "cyan" | "amber";
  emphasis?: boolean;
}

export function MetricCard({
  label,
  value,
  helper,
  source,
  unit,
  tone = "blue",
  emphasis,
}: MetricCardProps) {
  return (
    <article
      className={`metric-card metric-card--${tone}${
        emphasis ? " metric-card--emphasis" : ""
      }`}
    >
      <div className="metric-card__topline">
        <span>{label}</span>
        <i aria-hidden="true" />
      </div>
      <div className="metric-card__value">
        <strong>{value}</strong>
        {unit ? <em>{unit}</em> : null}
      </div>
      {helper ? <small>{helper}</small> : null}
      {source ? <div className="metric-card__source">Source: {source}</div> : null}
    </article>
  );
}
