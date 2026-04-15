from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from config import (  # noqa: E402
    build_bronze_batch_file_path,
    build_gold_output_file_path,
    build_silver_output_file_path,
)


def test_bronze_batch_path_uses_stream_date_and_batch_id() -> None:
    path = build_bronze_batch_file_path(stream_date="2026-04-15", batch_id="20260415T120000Z")

    assert str(path).endswith(
        "data/bronze/raw/stream_date=2026-04-15/batch_20260415T120000Z.jsonl"
    )


def test_silver_output_path_uses_event_date_and_batch_id() -> None:
    path = build_silver_output_file_path(event_date="2026-04-15", batch_id="20260415T120000Z")

    assert str(path).endswith(
        "data/silver/tables/recentchange_events/event_date=2026-04-15/batch_20260415T120000Z.parquet"
    )


def test_gold_output_path_uses_table_name_and_event_date_partition() -> None:
    path = build_gold_output_file_path(
        table_name="minute_event_summary",
        event_date="2026-04-15",
    )

    assert str(path).endswith(
        "data/gold/tables/minute_event_summary/event_date=2026-04-15/minute_event_summary.parquet"
    )
