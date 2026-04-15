from __future__ import annotations

from typing import Any

from config import path_relative_to_project


def build_gold_event_date_metadata(
    *,
    event_date: str,
    silver_source_glob: str,
    table_output_paths: dict[str, Any],
    table_row_counts: dict[str, int],
    started_at: str | None,
    finished_at: str | None,
) -> dict[str, Any]:
    """Build metadata for one Gold event-date refresh."""
    return {
        "event_date": event_date,
        "job_name": "gold",
        "silver_source_glob": silver_source_glob,
        "started_at": started_at,
        "finished_at": finished_at,
        "table_row_counts": table_row_counts,
        "table_output_files": {
            table_name: path_relative_to_project(path)
            for table_name, path in table_output_paths.items()
        },
    }
