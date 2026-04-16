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


def build_run_metadata_summary(
    *,
    layer: str,
    selected_months: list[str],
    results: list[dict[str, Any]],
    force: bool,
    run_started_at_utc: str,
    processed_statuses: set[str],
) -> dict[str, Any]:
    """Build a consistent latest-run summary for local operational review."""
    processed_months = [
        result["source_month"]
        for result in results
        if result.get("status") in processed_statuses
    ]
    skipped_months = [
        result["source_month"]
        for result in results
        if result.get("status") == "skipped"
    ]
    output_paths: list[str] = []
    for result in results:
        for path_key in ("output_path", "metadata_path"):
            path_value = result.get(path_key)
            if isinstance(path_value, str):
                output_paths.append(path_value)

        output_file_values = result.get("output_files")
        if isinstance(output_file_values, list):
            output_paths.extend(
                path for path in output_file_values if isinstance(path, str)
            )

    return {
        "project_name": get_settings().project_name,
        "layer": layer,
        "status": "completed",
        "run_started_at_utc": run_started_at_utc,
        "run_completed_at_utc": get_current_timestamp(),
        "selected_month_window": {
            "start_month": selected_months[0] if selected_months else None,
            "end_month": selected_months[-1] if selected_months else None,
            "month_count": len(selected_months),
        },
        "selected_months": selected_months,
        "processed_months": processed_months,
        "skipped_months": skipped_months,
        "processed_month_count": len(processed_months),
        "skipped_month_count": len(skipped_months),
        "force": force,
        "output_paths": sorted(set(output_paths)),
        "results": results,
    }
