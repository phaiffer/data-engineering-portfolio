from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from operations.validation import count_jsonl_rows, infer_validation_status  # noqa: E402


def test_count_jsonl_rows_ignores_blank_lines(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "batch.jsonl"
    jsonl_path.write_text('{"id": 1}\n\n{"id": 2}\n', encoding="utf-8")

    assert count_jsonl_rows(jsonl_path) == 2


def test_infer_validation_status_reports_gold_ready() -> None:
    manifest = {
        "bronze_files": {"batch_file_count": 1},
        "silver_files": {"parquet_file_count": 1},
        "gold_files": {
            "tables": {
                "minute_event_summary": {"parquet_file_count": 1},
                "event_type_summary": {"parquet_file_count": 0},
            }
        },
    }

    assert infer_validation_status(manifest) == "gold_ready"
