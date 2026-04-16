from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from config import (  # noqa: E402
    MonthPartition,
    build_bronze_raw_file_path,
    build_gold_output_file_path,
    build_silver_output_file_path,
    resolve_month_window,
)


def test_resolve_month_window_includes_cross_year_months() -> None:
    months = resolve_month_window(start_month="2024-11", end_month="2025-02")

    assert [month.month_id for month in months] == ["2024-11", "2024-12", "2025-01", "2025-02"]


def test_bronze_partition_path_uses_year_and_month() -> None:
    month = MonthPartition.from_string("2024-02")

    path = build_bronze_raw_file_path(month)

    assert path.as_posix().endswith("data/bronze/raw/yellow_taxi/year=2024/month=02/source.parquet")


def test_silver_and_gold_partition_paths_include_source_month_file_names() -> None:
    month = MonthPartition.from_string("2024-02")

    silver_path = build_silver_output_file_path(
        source_month=month,
        partition_year=2024,
        partition_month=2,
    )
    gold_path = build_gold_output_file_path(
        table_name="daily_trip_summary",
        source_month=month,
        partition_year=2024,
        partition_month=2,
    )

    assert silver_path.as_posix().endswith(
        "data/silver/tables/trips/pickup_year=2024/pickup_month=02/yellow_taxi_trips_2024-02.parquet"
    )
    assert gold_path.as_posix().endswith(
        "data/gold/tables/daily_trip_summary/pickup_year=2024/pickup_month=02/daily_trip_summary_2024-02.parquet"
    )
