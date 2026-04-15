import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCurrency, formatInteger } from "../../lib/format";

export type SummaryBarPoint = {
  label: string;
  count: number | null;
  value: number | null;
  valueLabel: string;
};

type TooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: SummaryBarPoint }>;
};

function SummaryTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.[0]) {
    return null;
  }

  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.label}</strong>
      <span>Count: {formatInteger(row.count)}</span>
      <span>
        {row.valueLabel}: {formatCurrency(row.value)}
      </span>
    </div>
  );
}

export function SummaryBarChart({
  rows,
  valueColor = "#2563eb",
}: {
  rows: SummaryBarPoint[];
  valueColor?: string;
}) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={rows} margin={{ top: 8, right: 16, bottom: 8, left: 8 }}>
        <CartesianGrid stroke="#e4ecef" strokeDasharray="4 8" vertical={false} />
        <XAxis
          dataKey="label"
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#22313a", fontSize: 11 }}
        />
        <YAxis
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#5f6f78", fontSize: 11 }}
          tickFormatter={(value: number) => formatCurrency(value)}
          width={76}
        />
        <Tooltip content={<SummaryTooltip />} cursor={{ fill: "#f2f6f7" }} />
        <Bar dataKey="value" fill={valueColor} radius={[6, 6, 0, 0]} maxBarSize={46} />
      </BarChart>
    </ResponsiveContainer>
  );
}
