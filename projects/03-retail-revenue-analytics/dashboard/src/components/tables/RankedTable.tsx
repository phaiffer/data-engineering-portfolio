import { formatCurrency, formatInteger } from "../../lib/format";

export type RankedTableRow = {
  label: string;
  context?: string;
  countLabel: string;
  count: number | null;
  revenue: number | null;
};

export function RankedTable({ rows }: { rows: RankedTableRow[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Context</th>
            <th>{rows[0]?.countLabel ?? "Count"}</th>
            <th>GMV</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={`${row.label}-${row.context ?? ""}`}>
              <td>{row.label}</td>
              <td>{row.context ?? "n/a"}</td>
              <td className="numeric-cell">{formatInteger(row.count)}</td>
              <td className="numeric-cell">{formatCurrency(row.revenue)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
