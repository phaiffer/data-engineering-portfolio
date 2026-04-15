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

export type RevenueBarPoint = {
  label: string;
  context?: string;
  count?: number | null;
  value: number | null;
};

type TooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: RevenueBarPoint }>;
};

function RevenueTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload?.[0]) {
    return null;
  }

  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{row.label}</strong>
      {row.context ? <span>{row.context}</span> : null}
      <span>GMV: {formatCurrency(row.value)}</span>
      {row.count !== undefined ? <span>Count: {formatInteger(row.count)}</span> : null}
    </div>
  );
}

export function RevenueBarChart({
  rows,
  height = 300,
}: {
  rows: RevenueBarPoint[];
  height?: number;
}) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={rows} layout="vertical" margin={{ top: 8, right: 16, bottom: 8, left: 20 }}>
        <CartesianGrid stroke="#e4ecef" strokeDasharray="4 8" horizontal={false} />
        <XAxis
          type="number"
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#5f6f78", fontSize: 11 }}
          tickFormatter={(value: number) => formatCurrency(value)}
        />
        <YAxis
          dataKey="label"
          type="category"
          width={118}
          tickLine={false}
          axisLine={false}
          tick={{ fill: "#22313a", fontSize: 11 }}
        />
        <Tooltip content={<RevenueTooltip />} cursor={{ fill: "#f2f6f7" }} />
        <Bar dataKey="value" fill="#0f766e" radius={[0, 6, 6, 0]} maxBarSize={24} />
      </BarChart>
    </ResponsiveContainer>
  );
}
