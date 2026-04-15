from __future__ import annotations

from typing import Any

import pandas as pd

from config import MonthPartition


def get_null_counts(dataframe: pd.DataFrame, columns: list[str]) -> dict[str, int]:
    """Return null counts for selected columns."""
    counts: dict[str, int] = {}
    for column in columns:
        if column not in dataframe.columns:
            continue
        counts[column] = int(dataframe[column].isna().sum())
    return counts


def get_negative_value_counts(dataframe: pd.DataFrame, columns: list[str]) -> dict[str, int]:
    """Return negative-value counts for selected numeric columns."""
    counts: dict[str, int] = {}
    for column in columns:
        if column not in dataframe.columns:
            continue
        counts[column] = int((dataframe[column] < 0).fillna(False).sum())
    return counts


def build_silver_quality_report(
    *,
    raw_dataframe: pd.DataFrame,
    silver_dataframe: pd.DataFrame,
    source_month: MonthPartition,
) -> dict[str, Any]:
    """Build row-preserving Silver checks without imposing strict business rules."""
    required_columns = [
        "pickup_datetime",
        "dropoff_datetime",
        "passenger_count",
        "trip_distance",
        "payment_type",
        "fare_amount",
        "total_amount",
        "source_year",
        "source_month",
    ]
    negative_value_columns = [
        "trip_distance",
        "fare_amount",
        "tip_amount",
        "tolls_amount",
        "total_amount",
    ]

    pickup_outside_source_month_count = 0
    if "pickup_datetime" in silver_dataframe.columns:
        pickup_period = pd.to_datetime(silver_dataframe["pickup_datetime"], errors="coerce")
        pickup_outside_source_month_count = int(
            (
                pickup_period.notna()
                & (
                    (pickup_period.dt.year != source_month.year)
                    | (pickup_period.dt.month != source_month.month)
                )
            ).sum()
        )
    invalid_trip_duration_count = 0
    if "trip_duration_minutes" in silver_dataframe.columns:
        invalid_trip_duration_count = int((silver_dataframe["trip_duration_minutes"] < 0).fillna(False).sum())

    return {
        "raw_row_count": int(len(raw_dataframe)),
        "silver_row_count": int(len(silver_dataframe)),
        "row_count_preserved": len(raw_dataframe) == len(silver_dataframe),
        "duplicate_row_count": int(silver_dataframe.duplicated().sum()),
        "null_counts": get_null_counts(silver_dataframe, required_columns),
        "negative_value_counts": get_negative_value_counts(silver_dataframe, negative_value_columns),
        "pickup_datetime_missing_count": int(silver_dataframe["pickup_datetime"].isna().sum())
        if "pickup_datetime" in silver_dataframe.columns
        else 0,
        "pickup_outside_source_month_count": pickup_outside_source_month_count,
        "invalid_trip_duration_count": invalid_trip_duration_count,
        "required_columns_present": all(column in silver_dataframe.columns for column in required_columns),
    }
