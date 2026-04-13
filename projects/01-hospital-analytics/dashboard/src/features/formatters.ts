const integerFormatter = new Intl.NumberFormat("en-US", {
  maximumFractionDigits: 0,
});

const decimalFormatter = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const percentFormatter = new Intl.NumberFormat("en-US", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const dateFormatter = new Intl.DateTimeFormat("en-US", {
  month: "short",
  day: "numeric",
});

export function formatInteger(value: number | null | undefined): string {
  return value == null ? "N/A" : integerFormatter.format(value);
}

export function formatDecimal(value: number | null | undefined): string {
  return value == null ? "N/A" : decimalFormatter.format(value);
}

export function formatPercent(value: number | null | undefined): string {
  return value == null ? "N/A" : percentFormatter.format(value);
}

export function formatDateLabel(value: string | null): string {
  if (!value) {
    return "Unknown";
  }

  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? value : dateFormatter.format(date);
}

export function formatNullableLabel(value: string | null | undefined): string {
  return value == null || value.trim() === "" ? "Unknown / Missing" : value;
}

