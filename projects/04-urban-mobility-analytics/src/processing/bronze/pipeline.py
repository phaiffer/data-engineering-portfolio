from __future__ import annotations

from typing import Any, Sequence

from config import (
    MonthPartition,
    build_bronze_raw_file_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
    resolve_month_window,
)
from ingestion.state import (
    get_month_entry,
    mark_month_completed,
    read_state,
    select_months_to_process,
    write_state,
)
from processing.bronze.metadata import (
    build_bronze_month_metadata,
    build_bronze_run_metadata,
    write_bronze_month_metadata,
    write_bronze_run_metadata,
)


def run_bronze_pipeline(
    *,
    months: Sequence[MonthPartition] | None = None,
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Build raw inventory and month-level metadata over landed Bronze files."""
    ensure_runtime_directories()
    settings = get_settings()
    selected_months = list(months or resolve_month_window(start_month=start_month, end_month=end_month))
    ingestion_state = read_state(settings.bronze_ingestion_state_path, "bronze_ingestion")
    bronze_state = read_state(settings.bronze_state_path, "bronze_metadata")
    months_to_profile = select_months_to_process(selected_months, bronze_state, force=force)
    months_to_profile_keys = {month.month_id for month in months_to_profile}

    results: list[dict[str, Any]] = []

    for month in selected_months:
        raw_path = build_bronze_raw_file_path(month)
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw Bronze file not found for {month.month_id}. Expected path: {raw_path}"
            )

        if month.month_id not in months_to_profile_keys:
            existing_entry = get_month_entry(bronze_state, month) or {}
            results.append(
                {
                    "source_month": month.month_id,
                    "status": "skipped",
                    "reason": "already_profiled",
                    "metadata_path": existing_entry.get("metadata_path"),
                }
            )
            continue

        metadata = build_bronze_month_metadata(
            month_partition=month,
            raw_path=raw_path,
            ingestion_entry=get_month_entry(ingestion_state, month),
        )
        metadata_path = write_bronze_month_metadata(metadata)

        bronze_state = mark_month_completed(
            bronze_state,
            month,
            {
                "metadata_path": path_relative_to_project(metadata_path),
                "row_count": metadata["row_count"],
                "column_count": metadata["column_count"],
            },
        )
        results.append(
            {
                "source_month": month.month_id,
                "status": "profiled",
                "metadata_path": path_relative_to_project(metadata_path),
                "row_count": metadata["row_count"],
                "column_count": metadata["column_count"],
            }
        )

    state_path = write_state(settings.bronze_state_path, bronze_state)
    run_metadata = build_bronze_run_metadata(
        selected_months=[month.month_id for month in selected_months],
        results=results,
        force=force,
    )
    run_metadata["state_path"] = path_relative_to_project(state_path)
    run_metadata_path = write_bronze_run_metadata(run_metadata)

    return {
        **run_metadata,
        "run_metadata_path": path_relative_to_project(run_metadata_path),
    }
