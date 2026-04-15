from __future__ import annotations

from typing import Any

import pandas as pd


def build_null_rate_summary(dataframe: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    """Return null-rate percentages for the requested columns."""
    if dataframe.empty:
        return {column: 1.0 for column in columns}

    summary: dict[str, float] = {}
    for column in columns:
        if column not in dataframe.columns:
            summary[column] = 1.0
            continue
        summary[column] = round(float(dataframe[column].isna().mean()), 4)
    return summary


def build_required_field_summary(dataframe: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, Any]]:
    """Return required-field completeness metrics."""
    row_count = len(dataframe.index)
    summary: dict[str, dict[str, Any]] = {}

    for column in columns:
        if column not in dataframe.columns:
            summary[column] = {"present": False, "non_null_count": 0, "null_count": row_count}
            continue

        non_null_count = int(dataframe[column].notna().sum())
        summary[column] = {
            "present": True,
            "non_null_count": non_null_count,
            "null_count": row_count - non_null_count,
        }

    return summary


def build_event_type_visibility(dataframe: pd.DataFrame) -> dict[str, int]:
    """Return visible event type counts for the standardized batch."""
    if dataframe.empty or "event_type" not in dataframe.columns:
        return {}

    counts = dataframe["event_type"].fillna("unknown").value_counts(dropna=False)
    return {str(index): int(value) for index, value in counts.items()}


def run_silver_quality_checks(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a concise quality summary for a standardized Silver dataframe."""
    required_fields = build_required_field_summary(
        dataframe,
        ["event_timestamp", "source_event_id", "event_type", "wiki"],
    )
    parseable_timestamp_count = required_fields["event_timestamp"]["non_null_count"]

    return {
        "row_count": int(len(dataframe.index)),
        "required_fields": required_fields,
        "parseable_timestamp_count": parseable_timestamp_count,
        "null_rates": build_null_rate_summary(dataframe, ["wiki", "namespace", "user_text", "comment_text"]),
        "event_type_visibility": build_event_type_visibility(dataframe),
    }
