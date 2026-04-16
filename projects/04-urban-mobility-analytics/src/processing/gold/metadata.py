from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import MonthPartition, get_settings, path_relative_to_project
from ingestion.state import build_run_metadata_summary


def build_gold_month_metadata(
    *,
    month_partition: MonthPartition,
    table_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build metadata for one month of Gold outputs."""
    return {
        "source_month": month_partition.month_id,
        "table_results": table_results,
        "table_count": len(table_results),
    }


def write_gold_month_metadata(metadata: dict[str, Any]) -> Path:
    """Write one month-level Gold metadata file."""
    settings = get_settings()
    output_path = settings.gold_metadata_dir / f"gold_month_{metadata['source_month']}.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def build_gold_run_metadata(
    *,
    selected_months: list[str],
    results: list[dict[str, Any]],
    force: bool,
    run_started_at_utc: str,
) -> dict[str, Any]:
    """Build the latest Gold run summary."""
    return build_run_metadata_summary(
        layer="gold",
        selected_months=selected_months,
        results=results,
        force=force,
        run_started_at_utc=run_started_at_utc,
        processed_statuses={"processed"},
    )


def write_gold_run_metadata(metadata: dict[str, Any]) -> Path:
    """Write the latest Gold run metadata."""
    settings = get_settings()
    output_path = settings.gold_metadata_dir / "latest_gold_run.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def describe_table_output(path: Path, row_count: int, column_count: int) -> dict[str, Any]:
    """Return lightweight serializable metadata for one Gold table output file."""
    return {
        "output_path": path_relative_to_project(path),
        "row_count": int(row_count),
        "column_count": int(column_count),
    }
