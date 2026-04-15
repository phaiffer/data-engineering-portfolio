from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.metrics import (  # noqa: E402
    classify_actor_segment,
    normalize_event_type,
    normalize_namespace,
)


def test_normalize_event_type_handles_case_and_missing_values() -> None:
    assert normalize_event_type("Edit") == "edit"
    assert normalize_event_type("  NEW ") == "new"
    assert normalize_event_type(None) == "unknown"


def test_classify_actor_segment_uses_bot_and_user_presence() -> None:
    assert classify_actor_segment(True, "SomeBot") == "bot"
    assert classify_actor_segment(False, "Alice") == "human"
    assert classify_actor_segment(None, None) == "unknown"


def test_normalize_namespace_returns_string_or_unknown() -> None:
    assert normalize_namespace(0) == "0"
    assert normalize_namespace("14") == "14"
    assert normalize_namespace(None) == "unknown"
