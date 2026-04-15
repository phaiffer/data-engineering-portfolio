import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { formatCurrency, formatInteger, formatShortDate } from "../../lib/format";
import type { DailyRevenueRow } from "../../types/api";

type TooltipProps = {
  active?: boolean;
  payload?: Array<{ payload: DailyRevenueRow }>;
  label?: string;
};

function DailyRevenueTooltip({ active, payload, label }: TooltipProps) {
  if (!active || !payload?.[0]) {
    return null;
  }

  const row = payload[0].payload;
  return (
    <div className="chart-tooltip">
      <strong>{formatShortDate(label)}</strong>
      <span>GMV: {formatCurrency(row.gross_merchandise_value)}</span>
      <span>Item revenue: {formatCurrency(row.item_revenue)}</span>
      <span>Orders: {formatInteger(row.order_count)}</span>
      <span>Status: {row.order_status}</span>
    </div>
  );
}

export function DailyRevenueChart({ rows }: { rows: DailyRevenueRow[] }) {
  return (
    <div className="chart-frame chart-frame--wide">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows} margin={{ top: 10, right: 20, bottom: 8, left: 8 }}>
          <CartesianGrid stroke="#d9e2e8" strokeDasharray="4 8" />
          <XAxis
            dataKey="order_purchase_date"
            minTickGap={24}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#5f6f78", fontSize: 11 }}
            tickFormatter={formatShortDate}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#5f6f78", fontSize: 11 }}
            tickFormatter={(value: number) => formatCurrency(value)}
            width={80}
          />
          <Tooltip content={<DailyRevenueTooltip />} />
          <Line
            type="monotone"
            dataKey="gross_merchandise_value"
            name="Gross merchandise value"
            stroke="#0f766e"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 5 }}
          />
          <Line
            type="monotone"
            dataKey="item_revenue"
            name="Item revenue"
            stroke="#2563eb"
            strokeWidth={1.8}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
