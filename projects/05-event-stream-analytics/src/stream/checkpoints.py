from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


def to_isoformat(value: datetime | None) -> str | None:
    """Serialize a datetime as an ISO-8601 UTC string."""
    if value is None:
        return None
    normalized = value.astimezone(timezone.utc).replace(microsecond=0)
    return normalized.isoformat().replace("+00:00", "Z")


def build_publisher_checkpoint_template() -> dict[str, Any]:
    """Return the default publisher checkpoint payload."""
    return {
        "checkpoint_type": "publisher",
        "last_sse_event_id": None,
        "last_source_meta_id": None,
        "last_event_timestamp": None,
        "last_publisher_run_id": None,
        "updated_at": None,
    }


def build_consumer_checkpoint_template(*, topic: str, consumer_group: str) -> dict[str, Any]:
    """Return the default Bronze consumer checkpoint payload."""
    return {
        "checkpoint_type": "bronze_consumer",
        "topic": topic,
        "consumer_group": consumer_group,
        "updated_at": None,
        "partition_offsets": {},
        "processed_batches": {},
    }


def build_layer_state_template(layer_name: str) -> dict[str, Any]:
    """Return a simple default state payload for Silver or Gold."""
    return {
        "layer": layer_name,
        "updated_at": None,
        "processed_batches": {},
        "processed_event_dates": {},
    }


def load_json_document(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    """Load a JSON document or return a deep-copied default payload."""
    if not path.exists():
        return json.loads(json.dumps(default))

    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json_document(path: Path, payload: dict[str, Any]) -> None:
    """Persist a JSON document with stable formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)


def update_publisher_checkpoint(
    checkpoint: dict[str, Any],
    *,
    run_id: str,
    sse_event_id: str | None,
    source_meta_id: str | None,
    event_timestamp: str | None,
) -> None:
    """Update the latest publisher checkpoint fields after a successful publish."""
    checkpoint["last_sse_event_id"] = sse_event_id
    checkpoint["last_source_meta_id"] = source_meta_id
    checkpoint["last_event_timestamp"] = event_timestamp
    checkpoint["last_publisher_run_id"] = run_id
    checkpoint["updated_at"] = to_isoformat(utc_now())


def update_partition_checkpoint(
    checkpoint: dict[str, Any],
    *,
    topic: str,
    partition: int,
    offset: int,
    broker_timestamp_ms: int | None,
) -> None:
    """Record the last landed offset for a topic partition."""
    key = f"{topic}:{partition}"
    checkpoint.setdefault("partition_offsets", {})
    checkpoint["partition_offsets"][key] = {
        "topic": topic,
        "partition": partition,
        "last_offset": offset,
        "last_timestamp_ms": broker_timestamp_ms,
    }
    checkpoint["updated_at"] = to_isoformat(utc_now())


def get_resume_offsets(checkpoint: dict[str, Any]) -> dict[tuple[str, int], int]:
    """Return the next offsets to consume for each partition."""
    offsets: dict[tuple[str, int], int] = {}
    for entry in checkpoint.get("partition_offsets", {}).values():
        topic = str(entry["topic"])
        partition = int(entry["partition"])
        last_offset = int(entry["last_offset"])
        offsets[(topic, partition)] = last_offset + 1
    return offsets


def should_stop_bounded_run(
    *,
    started_at: datetime,
    now: datetime,
    processed_count: int,
    max_events: int | None,
    max_seconds: int | None,
) -> str | None:
    """Return the stop reason for a bounded run, if one has been reached."""
    if max_events is not None and processed_count >= max_events:
        return "max_events_reached"

    if max_seconds is not None:
        elapsed_seconds = (now - started_at).total_seconds()
        if elapsed_seconds >= max_seconds:
            return "max_seconds_reached"

    return None
