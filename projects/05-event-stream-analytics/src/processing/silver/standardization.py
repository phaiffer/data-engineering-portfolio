from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd


PREFERRED_COLUMN_ORDER = [
    "source_batch_id",
    "source_meta_id",
    "source_event_id",
    "source_sse_event_id",
    "source_stream",
    "event_timestamp",
    "event_date",
    "event_hour",
    "event_minute",
    "event_type",
    "is_bot",
    "actor_segment",
    "is_minor",
    "is_patrolled",
    "wiki",
    "domain",
    "namespace",
    "title",
    "user_text",
    "comment_text",
    "server_name",
    "server_url",
    "log_type",
    "log_action",
    "length_old",
    "length_new",
    "revision_old",
    "revision_new",
    "broker_topic",
    "broker_partition",
    "broker_offset",
    "broker_timestamp_ms",
    "publisher_run_id",
    "published_at",
]


def parse_utc_timestamp(value: Any) -> datetime | None:
    """Safely parse a source timestamp into a naive UTC datetime."""
    if not value:
        return None
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return parsed.tz_convert("UTC").tz_localize(None).to_pydatetime()


def normalize_event_type(value: Any) -> str:
    """Return a normalized RecentChange event type label."""
    if value is None:
        return "unknown"
    normalized = str(value).strip().lower()
    return normalized or "unknown"


def classify_actor_segment(is_bot: Any, user_text: Any) -> str:
    """Classify the actor into a small, readable segment."""
    if is_bot is True:
        return "bot"
    if user_text:
        return "human"
    return "unknown"


def normalize_recentchange_record(record: dict[str, Any], *, source_batch_id: str) -> dict[str, Any]:
    """Flatten one raw Bronze record into a standardized Silver row."""
    event = record.get("event", {})
    meta = event.get("meta", {})
    revision = event.get("revision", {}) or {}
    length = event.get("length", {}) or {}

    event_timestamp = parse_utc_timestamp(meta.get("dt"))
    event_date = event_timestamp.date().isoformat() if event_timestamp else None
    event_hour = event_timestamp.hour if event_timestamp else None
    event_minute = event_timestamp.replace(second=0, microsecond=0) if event_timestamp else None

    is_bot = event.get("bot")
    if is_bot is not None:
        is_bot = bool(is_bot)

    return {
        "source_batch_id": source_batch_id,
        "source_meta_id": meta.get("id"),
        "source_event_id": event.get("id"),
        "source_sse_event_id": record.get("source", {}).get("sse_event_id"),
        "source_stream": meta.get("stream") or record.get("source", {}).get("source_stream"),
        "event_timestamp": event_timestamp,
        "event_date": event_date,
        "event_hour": event_hour,
        "event_minute": event_minute,
        "event_type": normalize_event_type(event.get("type")),
        "is_bot": is_bot,
        "actor_segment": classify_actor_segment(is_bot, event.get("user")),
        "is_minor": event.get("minor"),
        "is_patrolled": event.get("patrolled"),
        "wiki": event.get("wiki"),
        "domain": meta.get("domain"),
        "namespace": event.get("namespace"),
        "title": event.get("title"),
        "user_text": event.get("user"),
        "comment_text": event.get("comment"),
        "server_name": event.get("server_name"),
        "server_url": event.get("server_url"),
        "log_type": event.get("log_type"),
        "log_action": event.get("log_action"),
        "length_old": length.get("old"),
        "length_new": length.get("new"),
        "revision_old": revision.get("old"),
        "revision_new": revision.get("new"),
        "broker_topic": record.get("broker", {}).get("topic"),
        "broker_partition": record.get("broker", {}).get("partition"),
        "broker_offset": record.get("broker", {}).get("offset"),
        "broker_timestamp_ms": record.get("broker", {}).get("timestamp_ms"),
        "publisher_run_id": record.get("publisher", {}).get("publisher_run_id"),
        "published_at": parse_utc_timestamp(record.get("publisher", {}).get("published_at")),
    }


def standardize_recentchange_records(
    records: list[dict[str, Any]],
    *,
    source_batch_id: str,
) -> pd.DataFrame:
    """Return a row-preserving standardized dataframe for a Bronze batch."""
    rows = [normalize_recentchange_record(record, source_batch_id=source_batch_id) for record in records]
    dataframe = pd.DataFrame(rows)

    if dataframe.empty:
        return dataframe

    for column in ("event_timestamp", "event_minute", "published_at"):
        if column in dataframe.columns:
            dataframe[column] = pd.to_datetime(dataframe[column], errors="coerce")

    integer_columns = (
        "event_hour",
        "namespace",
        "length_old",
        "length_new",
        "revision_old",
        "revision_new",
        "broker_partition",
        "broker_offset",
        "broker_timestamp_ms",
        "source_event_id",
    )
    for column in integer_columns:
        if column in dataframe.columns:
            dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce").astype("Int64")

    boolean_columns = ("is_bot", "is_minor", "is_patrolled")
    for column in boolean_columns:
        if column in dataframe.columns:
            dataframe[column] = dataframe[column].astype("boolean")

    preferred = [column for column in PREFERRED_COLUMN_ORDER if column in dataframe.columns]
    remainder = [column for column in dataframe.columns if column not in preferred]
    return dataframe[preferred + remainder]
