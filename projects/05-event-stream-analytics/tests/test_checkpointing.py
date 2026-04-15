from __future__ import annotations

import sys
from datetime import timedelta
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from stream.checkpoints import (  # noqa: E402
    build_consumer_checkpoint_template,
    get_resume_offsets,
    load_json_document,
    save_json_document,
    should_stop_bounded_run,
    update_partition_checkpoint,
    utc_now,
)


def test_consumer_checkpoint_round_trip_preserves_partition_offsets(tmp_path: Path) -> None:
    checkpoint_path = tmp_path / "bronze_checkpoint.json"
    checkpoint = build_consumer_checkpoint_template(
        topic="wikimedia.recentchange.raw",
        consumer_group="bronze-test-group",
    )

    update_partition_checkpoint(
        checkpoint,
        topic="wikimedia.recentchange.raw",
        partition=0,
        offset=42,
        broker_timestamp_ms=1710000000000,
    )
    save_json_document(checkpoint_path, checkpoint)

    loaded = load_json_document(
        checkpoint_path,
        build_consumer_checkpoint_template(
            topic="wikimedia.recentchange.raw",
            consumer_group="bronze-test-group",
        ),
    )

    assert loaded["partition_offsets"]["wikimedia.recentchange.raw:0"]["last_offset"] == 42


def test_get_resume_offsets_returns_next_offset_per_partition() -> None:
    checkpoint = build_consumer_checkpoint_template(
        topic="wikimedia.recentchange.raw",
        consumer_group="bronze-test-group",
    )
    update_partition_checkpoint(
        checkpoint,
        topic="wikimedia.recentchange.raw",
        partition=2,
        offset=99,
        broker_timestamp_ms=1710000001234,
    )

    resume_offsets = get_resume_offsets(checkpoint)

    assert resume_offsets[("wikimedia.recentchange.raw", 2)] == 100


def test_should_stop_bounded_run_respects_event_limit_before_time_limit() -> None:
    started_at = utc_now() - timedelta(seconds=5)
    now = utc_now()

    stop_reason = should_stop_bounded_run(
        started_at=started_at,
        now=now,
        processed_count=10,
        max_events=10,
        max_seconds=60,
    )

    assert stop_reason == "max_events_reached"
