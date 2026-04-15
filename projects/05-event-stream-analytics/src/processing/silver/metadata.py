from __future__ import annotations

from typing import Any

from config import path_relative_to_project


def build_silver_batch_metadata(
    *,
    batch_id: str,
    source_path,
    output_paths: list,
    quality_summary: dict[str, Any],
    started_at: str | None,
    finished_at: str | None,
) -> dict[str, Any]:
    """Build the metadata payload for one standardized Bronze batch."""
    return {
        "batch_id": batch_id,
        "job_name": "silver",
        "source_batch_path": path_relative_to_project(source_path),
        "started_at": started_at,
        "finished_at": finished_at,
        "row_count": quality_summary["row_count"],
        "event_dates_written": sorted(
            {
                output_path.parent.name.replace("event_date=", "")
                for output_path in output_paths
            }
        ),
        "output_files": [path_relative_to_project(output_path) for output_path in output_paths],
        "quality": quality_summary,
    }
