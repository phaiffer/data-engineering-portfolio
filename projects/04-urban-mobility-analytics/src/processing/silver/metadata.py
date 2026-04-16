from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from config import MonthPartition, get_settings, path_relative_to_project
from ingestion.state import build_run_metadata_summary


def build_silver_month_metadata(
    *,
    month_partition: MonthPartition,
    output_files: list[Path],
    partition_details: list[dict[str, Any]],
    quality_report: dict[str, Any],
) -> dict[str, Any]:
    """Build metadata for one standardized Silver month."""
    return {
        "source_month": month_partition.month_id,
        "output_files": [path_relative_to_project(path) for path in output_files],
        "output_file_count": len(output_files),
        "partition_details": partition_details,
        "quality_report": quality_report,
    }


def write_silver_month_metadata(metadata: dict[str, Any]) -> Path:
    """Write one month-level Silver metadata file."""
    settings = get_settings()
    output_path = settings.silver_metadata_dir / f"silver_month_{metadata['source_month']}.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def build_silver_run_metadata(
    *,
    selected_months: list[str],
    results: list[dict[str, Any]],
    force: bool,
    run_started_at_utc: str,
) -> dict[str, Any]:
    """Build the latest run summary for the Silver layer."""
    return build_run_metadata_summary(
        layer="silver",
        selected_months=selected_months,
        results=results,
        force=force,
        run_started_at_utc=run_started_at_utc,
        processed_statuses={"processed"},
    )


def write_silver_run_metadata(metadata: dict[str, Any]) -> Path:
    """Write the latest Silver run summary."""
    settings = get_settings()
    output_path = settings.silver_metadata_dir / "latest_silver_run.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path
