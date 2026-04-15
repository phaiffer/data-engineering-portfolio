from __future__ import annotations

from collections import Counter
from typing import Any

from config import path_relative_to_project


def summarize_event_types(records: list[dict[str, Any]]) -> dict[str, int]:
    """Return event type counts for a landed raw batch."""
    counts = Counter()
    for record in records:
        event_type = record.get("event", {}).get("type") or "unknown"
        counts[str(event_type)] += 1
    return dict(sorted(counts.items()))


def summarize_time_range(records: list[dict[str, Any]]) -> dict[str, str | None]:
    """Return the min and max source event timestamps found in the batch."""
    timestamps = [
        record.get("event", {}).get("meta", {}).get("dt")
        for record in records
        if record.get("event", {}).get("meta", {}).get("dt")
    ]
    if not timestamps:
        return {"min_event_timestamp": None, "max_event_timestamp": None}
    return {
        "min_event_timestamp": min(timestamps),
        "max_event_timestamp": max(timestamps),
    }


def build_bronze_batch_metadata(
    *,
    batch_id: str,
    batch_path,
    records: list[dict[str, Any]],
    started_at: str | None,
    finished_at: str | None,
    max_events: int | None,
    max_seconds: int | None,
    resume_strategy: str,
    stop_reason: str | None,
    observed_partitions: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build a stable metadata payload for one Bronze landing batch."""
    time_range = summarize_time_range(records)
    return {
        "batch_id": batch_id,
        "job_name": "bronze_consumer",
        "batch_path": path_relative_to_project(batch_path),
        "started_at": started_at,
        "finished_at": finished_at,
        "max_events": max_events,
        "max_seconds": max_seconds,
        "resume_strategy": resume_strategy,
        "stop_reason": stop_reason,
        "landed_event_count": len(records),
        "event_type_counts": summarize_event_types(records),
        "observed_partitions": list(observed_partitions.values()),
        **time_range,
    }
