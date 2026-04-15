from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from stream.checkpoints import to_isoformat, utc_now


def make_run_id(at: datetime | None = None) -> str:
    """Return a readable UTC timestamp identifier for runs and batch ids."""
    value = at or utc_now()
    return value.strftime("%Y%m%dT%H%M%SZ")


def build_message_key(event_payload: dict[str, Any]) -> str:
    """Return a stable Kafka message key when the source provides one."""
    meta_id = event_payload.get("meta", {}).get("id")
    event_id = event_payload.get("id")
    wiki = event_payload.get("wiki")

    if meta_id:
        return str(meta_id)
    if event_id is not None:
        return str(event_id)
    if wiki:
        return f"{wiki}:{uuid.uuid4().hex}"
    return uuid.uuid4().hex


def is_canary_event(event_payload: dict[str, Any]) -> bool:
    """Return whether the Wikimedia event is a synthetic canary event."""
    return event_payload.get("meta", {}).get("domain") == "canary"


def build_broker_message(
    event_payload: dict[str, Any],
    *,
    sse_event_id: str | None,
    publisher_run_id: str,
    source_url: str,
    published_at: datetime | None = None,
) -> dict[str, Any]:
    """Wrap a raw Wikimedia event with publish-time metadata."""
    published_timestamp = published_at or utc_now()
    return {
        "source": {
            "source_url": source_url,
            "source_stream": event_payload.get("meta", {}).get("stream"),
            "sse_event_id": sse_event_id,
            "source_meta_id": event_payload.get("meta", {}).get("id"),
        },
        "publisher": {
            "publisher_run_id": publisher_run_id,
            "published_at": to_isoformat(published_timestamp),
            "message_key": build_message_key(event_payload),
        },
        "event": event_payload,
    }


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    """Write one JSON document per line."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=False))
            handle.write("\n")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load newline-delimited JSON records from disk."""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records
