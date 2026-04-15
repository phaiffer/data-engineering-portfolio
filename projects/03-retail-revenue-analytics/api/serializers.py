from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any


def serialize_value(value: Any) -> Any:
    """Convert database values into JSON-friendly Python values."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert one database row into a JSON-friendly dictionary."""
    return {key: serialize_value(value) for key, value in row.items()}


def serialize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert database rows into JSON-friendly dictionaries."""
    return [serialize_row(row) for row in rows]
