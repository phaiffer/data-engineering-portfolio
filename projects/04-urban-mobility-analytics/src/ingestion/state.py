from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import MonthPartition, get_settings


def get_current_timestamp() -> str:
    """Return a timezone-aware UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat()


def build_state_template(layer: str) -> dict[str, Any]:
    """Create the default state structure for one pipeline layer."""
    settings = get_settings()
    return {
        "project_name": settings.project_name,
        "layer": layer,
        "last_updated_utc": None,
        "completed_months": {},
    }


def read_state(state_path: Path, layer: str) -> dict[str, Any]:
    """Load a state file or return an empty default state."""
    if not state_path.exists():
        return build_state_template(layer)

    with state_path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)

    state.setdefault("project_name", get_settings().project_name)
    state.setdefault("layer", layer)
    state.setdefault("last_updated_utc", None)
    state.setdefault("completed_months", {})
    return state


def write_state(state_path: Path, state: dict[str, Any]) -> Path:
    """Persist a state structure as readable JSON."""
    state["last_updated_utc"] = get_current_timestamp()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state_path


def month_key(month_partition: MonthPartition) -> str:
    """Return the canonical key used in state manifests."""
    return month_partition.month_id


def get_month_entry(
    state: dict[str, Any],
    month_partition: MonthPartition,
) -> dict[str, Any] | None:
    """Return the stored state entry for one month, when present."""
    return state.get("completed_months", {}).get(month_key(month_partition))


def is_month_completed(state: dict[str, Any], month_partition: MonthPartition) -> bool:
    """Return whether one month is already marked complete."""
    entry = get_month_entry(state, month_partition)
    return bool(entry and entry.get("status") == "completed")


def select_months_to_process(
    months: list[MonthPartition],
    state: dict[str, Any],
    *,
    force: bool = False,
) -> list[MonthPartition]:
    """Return the months that still need processing for a layer."""
    if force:
        return list(months)

    return [month for month in months if not is_month_completed(state, month)]


def mark_month_completed(
    state: dict[str, Any],
    month_partition: MonthPartition,
    details: dict[str, Any],
) -> dict[str, Any]:
    """Upsert a successful month record into a layer state manifest."""
    entry = {
        "status": "completed",
        "completed_at_utc": get_current_timestamp(),
        **details,
    }
    state.setdefault("completed_months", {})[month_key(month_partition)] = entry
    return state
