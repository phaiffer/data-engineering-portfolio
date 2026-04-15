from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.metrics import (  # noqa: E402
    classify_fare_amount,
    classify_trip_distance,
    map_payment_type,
    safe_divide,
)


def test_safe_divide_returns_zero_for_zero_denominator() -> None:
    assert safe_divide(10, 0) == 0.0


def test_classify_trip_distance_uses_expected_bucket_labels() -> None:
    assert classify_trip_distance(0.5) == "0_to_1_miles"
    assert classify_trip_distance(2.5) == "1_to_3_miles"
    assert classify_trip_distance(20) == "15_plus_miles"
    assert classify_trip_distance(-1) == "invalid_negative_distance"


def test_classify_fare_amount_uses_expected_bucket_labels() -> None:
    assert classify_fare_amount(8) == "0_to_10_usd"
    assert classify_fare_amount(35) == "25_to_50_usd"
    assert classify_fare_amount(120) == "100_plus_usd"
    assert classify_fare_amount(-5) == "invalid_negative_fare"


def test_map_payment_type_uses_tlc_labels() -> None:
    assert map_payment_type(1) == "credit_card"
    assert map_payment_type(2) == "cash"
    assert map_payment_type(99) == "unknown"
