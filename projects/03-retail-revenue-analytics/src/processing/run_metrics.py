from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).isoformat()


def build_run_metrics(
    *,
    job_name: str,
    status: str,
    started_at_utc: str,
    rows_read: int,
    rows_written: int,
    invalid_row_count: int = 0,
    rejected_row_count: int = 0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a lightweight structured metrics payload for local batch jobs."""
    ended_at_utc = utc_now_iso()
    metrics: dict[str, Any] = {
        "job_name": job_name,
        "status": status,
        "started_at_utc": started_at_utc,
        "ended_at_utc": ended_at_utc,
        "rows_read": int(rows_read),
        "rows_written": int(rows_written),
        "invalid_row_count": int(invalid_row_count),
        "rejected_row_count": int(rejected_row_count),
    }
    if extra:
        metrics.update(extra)
    return metrics
