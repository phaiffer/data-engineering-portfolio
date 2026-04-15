from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from config import (
    MonthPartition,
    build_bronze_raw_file_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
    resolve_month_window,
)
from ingestion.download import download_file, fetch_remote_metadata
from ingestion.state import (
    get_current_timestamp,
    get_month_entry,
    mark_month_completed,
    read_state,
    select_months_to_process,
    write_state,
)


def build_yellow_taxi_source_url(month_partition: MonthPartition) -> str:
    """Return the official monthly Yellow Taxi download URL."""
    settings = get_settings()
    return (
        f"{settings.source_base_url}/"
        f"yellow_tripdata_{month_partition.year:04d}-{month_partition.month:02d}.parquet"
    )


def build_download_plan(
    months: Sequence[MonthPartition],
    *,
    force: bool = False,
) -> list[dict[str, Any]]:
    """Create a readable month-by-month ingestion plan."""
    settings = get_settings()
    state = read_state(settings.bronze_ingestion_state_path, "bronze_ingestion")
    months_to_download = {
        month.month_id for month in select_months_to_process(list(months), state, force=force)
    }

    plan: list[dict[str, Any]] = []
    for month in months:
        output_path = build_bronze_raw_file_path(month)
        plan.append(
            {
                "source_month": month.month_id,
                "source_url": build_yellow_taxi_source_url(month),
                "output_path": path_relative_to_project(output_path),
                "already_completed": month.month_id not in months_to_download,
                "should_download": month.month_id in months_to_download,
            }
        )

    return plan


def _write_ingestion_run_metadata(metadata: dict[str, Any]) -> Path:
    settings = get_settings()
    output_path = settings.bronze_metadata_dir / "latest_ingestion_run.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def run_ingestion_pipeline(
    *,
    months: Sequence[MonthPartition] | None = None,
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Land official NYC TLC monthly Parquet files into the Bronze raw area."""
    ensure_runtime_directories()
    settings = get_settings()
    selected_months = list(months or resolve_month_window(start_month=start_month, end_month=end_month))

    state = read_state(settings.bronze_ingestion_state_path, "bronze_ingestion")
    months_to_download = select_months_to_process(selected_months, state, force=force)
    months_to_download_keys = {month.month_id for month in months_to_download}

    results: list[dict[str, Any]] = []

    for month in selected_months:
        output_path = build_bronze_raw_file_path(month)
        source_url = build_yellow_taxi_source_url(month)

        if month.month_id not in months_to_download_keys:
            existing_entry = get_month_entry(state, month) or {}
            results.append(
                {
                    "source_month": month.month_id,
                    "status": "skipped",
                    "reason": "already_completed",
                    "source_url": source_url,
                    "output_path": path_relative_to_project(output_path),
                    "downloaded_bytes": existing_entry.get("downloaded_bytes"),
                    "sha256": existing_entry.get("sha256"),
                }
            )
            continue

        if force and output_path.exists():
            output_path.unlink()

        downloaded_at_utc = get_current_timestamp()
        remote_metadata = fetch_remote_metadata(
            source_url,
            timeout_seconds=settings.request_timeout_seconds,
        )
        download_result = download_file(
            url=source_url,
            output_path=output_path,
            timeout_seconds=settings.request_timeout_seconds,
            chunk_size_bytes=settings.download_chunk_size_bytes,
            downloaded_at_utc=downloaded_at_utc,
        )

        state = mark_month_completed(
            state,
            month,
            {
                "source_url": source_url,
                "output_path": path_relative_to_project(output_path),
                "downloaded_bytes": download_result.downloaded_bytes,
                "sha256": download_result.sha256,
                "content_length": download_result.content_length or remote_metadata["content_length"],
                "etag": download_result.etag or remote_metadata["etag"],
                "last_modified": download_result.last_modified or remote_metadata["last_modified"],
            },
        )

        result_details = download_result.to_dict()
        result_details["output_path"] = path_relative_to_project(output_path)
        results.append(
            {
                "source_month": month.month_id,
                "status": "downloaded",
                "source_url": source_url,
                **result_details,
            }
        )

    state_path = write_state(settings.bronze_ingestion_state_path, state)
    run_metadata = {
        "project_name": settings.project_name,
        "layer": "bronze_ingestion",
        "selected_months": [month.month_id for month in selected_months],
        "downloaded_month_count": sum(1 for result in results if result["status"] == "downloaded"),
        "skipped_month_count": sum(1 for result in results if result["status"] == "skipped"),
        "force": force,
        "results": results,
        "state_path": path_relative_to_project(state_path),
    }
    run_metadata_path = _write_ingestion_run_metadata(run_metadata)

    return {
        **run_metadata,
        "run_metadata_path": path_relative_to_project(run_metadata_path),
    }
