from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from config import MonthPartition  # noqa: E402
from ingestion.state import (  # noqa: E402
    build_state_template,
    is_month_completed,
    mark_month_completed,
    select_months_to_process,
)


def test_select_months_to_process_skips_completed_months_by_default() -> None:
    january = MonthPartition.from_string("2024-01")
    february = MonthPartition.from_string("2024-02")
    state = build_state_template("silver")
    mark_month_completed(state, january, {"metadata_path": "data/silver/metadata/silver_month_2024-01.json"})

    pending = select_months_to_process([january, february], state, force=False)

    assert pending == [february]


def test_select_months_to_process_respects_force() -> None:
    january = MonthPartition.from_string("2024-01")
    february = MonthPartition.from_string("2024-02")
    state = build_state_template("gold")
    mark_month_completed(state, january, {"metadata_path": "data/gold/metadata/gold_month_2024-01.json"})

    pending = select_months_to_process([january, february], state, force=True)

    assert pending == [january, february]


def test_mark_month_completed_updates_completion_status() -> None:
    march = MonthPartition.from_string("2024-03")
    state = build_state_template("bronze_metadata")

    mark_month_completed(state, march, {"row_count": 123456})

    assert is_month_completed(state, march) is True
    assert state["completed_months"]["2024-03"]["row_count"] == 123456
