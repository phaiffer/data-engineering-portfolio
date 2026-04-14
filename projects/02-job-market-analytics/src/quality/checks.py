from __future__ import annotations

from typing import Any

import pandas as pd


def get_null_counts(dataframe: pd.DataFrame) -> dict[str, int]:
    """Return null counts by column as plain Python integers."""
    return {column: int(count) for column, count in dataframe.isna().sum().items()}


def get_null_rates(dataframe: pd.DataFrame) -> dict[str, float]:
    """Return null rates by column."""
    if len(dataframe) == 0:
        return {column: 0.0 for column in dataframe.columns}

    return {column: float(count / len(dataframe)) for column, count in dataframe.isna().sum().items()}


def summarize_numeric_columns(dataframe: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, Any]]:
    """Return lightweight numeric profiling for selected columns."""
    summary: dict[str, dict[str, Any]] = {}
    for column in columns:
        if column not in dataframe.columns:
            continue

        series = dataframe[column]
        summary[column] = {
            "non_null_count": int(series.notna().sum()),
            "null_count": int(series.isna().sum()),
            "min": None if series.dropna().empty else float(series.min()),
            "max": None if series.dropna().empty else float(series.max()),
            "mean": None if series.dropna().empty else float(series.mean()),
        }

    return summary


def validate_silver_dataframe(
    *,
    raw_dataframe: pd.DataFrame,
    silver_dataframe: pd.DataFrame,
    expected_columns: list[str],
) -> dict[str, Any]:
    """Return lightweight validation results for the Silver output."""
    missing_columns = [column for column in expected_columns if column not in silver_dataframe.columns]
    extra_columns = [column for column in silver_dataframe.columns if column not in expected_columns]
    row_count_preserved = len(raw_dataframe) == len(silver_dataframe)
    null_rates = get_null_rates(silver_dataframe)

    return {
        "raw_row_count": int(len(raw_dataframe)),
        "silver_row_count": int(len(silver_dataframe)),
        "row_count_preserved": row_count_preserved,
        "expected_columns": expected_columns,
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "duplicate_row_count": int(silver_dataframe.duplicated().sum()),
        "null_counts": get_null_counts(silver_dataframe),
        "null_rates": null_rates,
        "null_heavy_columns": {
            column: rate for column, rate in null_rates.items() if rate >= 0.25
        },
        "numeric_summary": summarize_numeric_columns(silver_dataframe, ["salary_usd"]),
        "is_valid": row_count_preserved and not missing_columns and not extra_columns,
    }
