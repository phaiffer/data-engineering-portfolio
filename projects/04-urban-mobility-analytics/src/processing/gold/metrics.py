from __future__ import annotations

import math
from typing import Iterable


PAYMENT_TYPE_LABELS = {
    0: "flex_fare",
    1: "credit_card",
    2: "cash",
    3: "no_charge",
    4: "dispute",
    5: "unknown",
    6: "voided_trip",
}

TRIP_DISTANCE_BUCKETS = [
    (0.0, 1.0, "0_to_1_miles"),
    (1.0, 3.0, "1_to_3_miles"),
    (3.0, 7.0, "3_to_7_miles"),
    (7.0, 15.0, "7_to_15_miles"),
    (15.0, None, "15_plus_miles"),
]

FARE_AMOUNT_BUCKETS = [
    (0.0, 10.0, "0_to_10_usd"),
    (10.0, 25.0, "10_to_25_usd"),
    (25.0, 50.0, "25_to_50_usd"),
    (50.0, 100.0, "50_to_100_usd"),
    (100.0, None, "100_plus_usd"),
]


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, float):
        return math.isnan(value)
    return False


def safe_divide(numerator: float, denominator: float, *, precision: int = 2) -> float:
    """Return a rounded division result without raising on zero denominators."""
    if denominator == 0:
        return 0.0
    return round(numerator / denominator, precision)


def map_payment_type(payment_type_code: int | float | None) -> str:
    """Return a readable payment label using the TLC dictionary codes."""
    if _is_missing(payment_type_code):
        return "unknown"

    try:
        normalized = int(payment_type_code)
    except (TypeError, ValueError):
        return "unknown"

    return PAYMENT_TYPE_LABELS.get(normalized, "unknown")


def _classify_bucket(
    value: float | int | None,
    *,
    buckets: Iterable[tuple[float, float | None, str]],
    null_label: str,
    negative_label: str,
) -> str:
    if _is_missing(value):
        return null_label

    numeric_value = float(value)
    if numeric_value < 0:
        return negative_label

    for lower_bound, upper_bound, label in buckets:
        if upper_bound is None and numeric_value >= lower_bound:
            return label
        if upper_bound is not None and lower_bound <= numeric_value < upper_bound:
            return label

    return null_label


def classify_trip_distance(distance: float | int | None) -> str:
    """Classify a trip distance into a small set of inspectable operational buckets."""
    return _classify_bucket(
        distance,
        buckets=TRIP_DISTANCE_BUCKETS,
        null_label="unknown_distance",
        negative_label="invalid_negative_distance",
    )


def classify_fare_amount(fare_amount: float | int | None) -> str:
    """Classify fare amount into a small set of readable operational buckets."""
    return _classify_bucket(
        fare_amount,
        buckets=FARE_AMOUNT_BUCKETS,
        null_label="unknown_fare",
        negative_label="invalid_negative_fare",
    )


def build_payment_type_case_sql(column_name: str) -> str:
    """Build a DuckDB CASE expression that maps TLC payment codes to labels."""
    lines = ["CASE"]
    lines.append(f"    WHEN {column_name} IS NULL THEN 'unknown'")
    for code, label in PAYMENT_TYPE_LABELS.items():
        lines.append(f"    WHEN CAST({column_name} AS INTEGER) = {code} THEN '{label}'")
    lines.append("    ELSE 'unknown'")
    lines.append("END")
    return "\n".join(lines)


def build_trip_distance_bucket_case_sql(column_name: str) -> str:
    """Build a DuckDB CASE expression for trip distance bucketing."""
    return "\n".join(
        [
            "CASE",
            f"    WHEN {column_name} IS NULL THEN 'unknown_distance'",
            f"    WHEN {column_name} < 0 THEN 'invalid_negative_distance'",
            f"    WHEN {column_name} < 1 THEN '0_to_1_miles'",
            f"    WHEN {column_name} < 3 THEN '1_to_3_miles'",
            f"    WHEN {column_name} < 7 THEN '3_to_7_miles'",
            f"    WHEN {column_name} < 15 THEN '7_to_15_miles'",
            "    ELSE '15_plus_miles'",
            "END",
        ]
    )


def build_fare_amount_bucket_case_sql(column_name: str) -> str:
    """Build a DuckDB CASE expression for fare amount bucketing."""
    return "\n".join(
        [
            "CASE",
            f"    WHEN {column_name} IS NULL THEN 'unknown_fare'",
            f"    WHEN {column_name} < 0 THEN 'invalid_negative_fare'",
            f"    WHEN {column_name} < 10 THEN '0_to_10_usd'",
            f"    WHEN {column_name} < 25 THEN '10_to_25_usd'",
            f"    WHEN {column_name} < 50 THEN '25_to_50_usd'",
            f"    WHEN {column_name} < 100 THEN '50_to_100_usd'",
            "    ELSE '100_plus_usd'",
            "END",
        ]
    )
