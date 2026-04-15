from __future__ import annotations

from typing import Any


def normalize_event_type(value: Any) -> str:
    """Return a normalized event type label."""
    if value is None:
        return "unknown"
    normalized = str(value).strip().lower()
    return normalized or "unknown"


def classify_actor_segment(is_bot: Any, user_text: Any) -> str:
    """Classify the actor segment in a small and readable way."""
    if is_bot is True:
        return "bot"
    if user_text:
        return "human"
    return "unknown"


def normalize_namespace(value: Any) -> str:
    """Return a readable namespace label for summary tables."""
    if value is None:
        return "unknown"
    try:
        return str(int(value))
    except (TypeError, ValueError):
        return "unknown"


def actor_segment_case_sql(*, is_bot_column: str = "is_bot", user_column: str = "user_text") -> str:
    """Build a DuckDB CASE expression for actor segment classification."""
    return "\n".join(
        [
            "CASE",
            f"    WHEN {is_bot_column} IS TRUE THEN 'bot'",
            f"    WHEN {user_column} IS NOT NULL AND TRIM(CAST({user_column} AS VARCHAR)) <> '' THEN 'human'",
            "    ELSE 'unknown'",
            "END",
        ]
    )


def namespace_case_sql(column_name: str = "namespace") -> str:
    """Build a DuckDB CASE expression for namespace labeling."""
    return "\n".join(
        [
            "CASE",
            f"    WHEN {column_name} IS NULL THEN 'unknown'",
            f"    ELSE CAST({column_name} AS VARCHAR)",
            "END",
        ]
    )
