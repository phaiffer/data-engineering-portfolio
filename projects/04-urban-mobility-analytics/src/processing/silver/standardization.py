from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from config import MonthPartition


COLUMN_RENAMES = {
    "vendorid": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "ratecodeid": "rate_code_id",
    "pulocationid": "pickup_location_id",
    "dolocationid": "dropoff_location_id",
    "extra": "extra_amount",
}

DATETIME_COLUMNS = ("pickup_datetime", "dropoff_datetime")
NUMERIC_COLUMNS = (
    "vendor_id",
    "passenger_count",
    "trip_distance",
    "rate_code_id",
    "pickup_location_id",
    "dropoff_location_id",
    "payment_type",
    "fare_amount",
    "extra_amount",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
)
INTEGER_COLUMNS = (
    "vendor_id",
    "passenger_count",
    "rate_code_id",
    "pickup_location_id",
    "dropoff_location_id",
    "payment_type",
    "pickup_year",
    "pickup_month",
    "pickup_day",
    "pickup_hour",
    "source_year",
    "source_month",
)
PREFERRED_COLUMN_ORDER = [
    "vendor_id",
    "pickup_datetime",
    "dropoff_datetime",
    "pickup_date",
    "pickup_year",
    "pickup_month",
    "pickup_day",
    "pickup_hour",
    "trip_duration_minutes",
    "passenger_count",
    "trip_distance",
    "rate_code_id",
    "store_and_fwd_flag",
    "pickup_location_id",
    "dropoff_location_id",
    "payment_type",
    "fare_amount",
    "extra_amount",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee",
    "source_year",
    "source_month",
    "source_month_id",
]


def normalize_column_name(column_name: str) -> str:
    """Normalize source column names into lowercase snake_case."""
    normalized = column_name.strip()
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", normalized)
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").lower()


def normalize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataframe with normalized column names."""
    normalized = dataframe.copy()
    normalized.columns = [normalize_column_name(column) for column in normalized.columns]
    return normalized


def standardize_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Trim string columns while preserving row grain."""
    standardized = dataframe.copy()
    text_columns = standardized.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        standardized[column] = standardized[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        standardized[column] = standardized[column].replace("", pd.NA)

    return standardized


def parse_datetime_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Safely parse configured datetime columns."""
    parsed = dataframe.copy()
    for column in columns:
        if column in parsed.columns:
            parsed[column] = pd.to_datetime(parsed[column], errors="coerce")
    return parsed


def parse_numeric_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Safely parse configured numeric columns."""
    parsed = dataframe.copy()
    for column in columns:
        if column in parsed.columns:
            parsed[column] = pd.to_numeric(parsed[column], errors="coerce")
    return parsed


def order_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Keep the most important columns front-loaded and stable."""
    preferred = [column for column in PREFERRED_COLUMN_ORDER if column in dataframe.columns]
    remaining = [column for column in dataframe.columns if column not in preferred]
    return dataframe[preferred + remaining]


def standardize_yellow_taxi_dataframe(
    dataframe: pd.DataFrame,
    *,
    source_month: MonthPartition,
) -> pd.DataFrame:
    """Apply safe row-preserving standardization to Yellow Taxi trip records."""
    standardized = normalize_column_names(dataframe)
    standardized = standardized.rename(columns=COLUMN_RENAMES)
    standardized = standardize_text_columns(standardized)
    standardized = parse_datetime_columns(standardized, DATETIME_COLUMNS)
    standardized = parse_numeric_columns(standardized, NUMERIC_COLUMNS)

    if "pickup_datetime" in standardized.columns:
        standardized["pickup_date"] = standardized["pickup_datetime"].dt.date
        standardized["pickup_year"] = standardized["pickup_datetime"].dt.year.astype("Int64")
        standardized["pickup_month"] = standardized["pickup_datetime"].dt.month.astype("Int64")
        standardized["pickup_day"] = standardized["pickup_datetime"].dt.day.astype("Int64")
        standardized["pickup_hour"] = standardized["pickup_datetime"].dt.hour.astype("Int64")
    else:
        standardized["pickup_date"] = pd.NA
        standardized["pickup_year"] = pd.Series([pd.NA] * len(standardized), dtype="Int64")
        standardized["pickup_month"] = pd.Series([pd.NA] * len(standardized), dtype="Int64")
        standardized["pickup_day"] = pd.Series([pd.NA] * len(standardized), dtype="Int64")
        standardized["pickup_hour"] = pd.Series([pd.NA] * len(standardized), dtype="Int64")

    if {"pickup_datetime", "dropoff_datetime"}.issubset(standardized.columns):
        standardized["trip_duration_minutes"] = (
            (
                standardized["dropoff_datetime"] - standardized["pickup_datetime"]
            ).dt.total_seconds()
            / 60.0
        ).round(2)

    standardized["source_year"] = source_month.year
    standardized["source_month"] = source_month.month
    standardized["source_month_id"] = source_month.month_id

    for column in INTEGER_COLUMNS:
        if column in standardized.columns:
            standardized[column] = standardized[column].astype("Int64")

    return order_columns(standardized)
