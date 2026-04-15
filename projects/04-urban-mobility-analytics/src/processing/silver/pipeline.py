from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import pandas as pd

from config import (
    MonthPartition,
    build_bronze_raw_file_path,
    build_silver_output_file_path,
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
from processing.silver.metadata import (
    build_silver_month_metadata,
    build_silver_run_metadata,
    write_silver_month_metadata,
    write_silver_run_metadata,
)
from processing.silver.standardization import standardize_yellow_taxi_dataframe
from quality.checks import build_silver_quality_report


def _clear_existing_month_outputs(source_month: MonthPartition) -> None:
    settings = get_settings()
    pattern = f"{settings.dataset_slug}_trips_{source_month.month_id}.parquet"
    for path in (settings.silver_tables_dir / "trips").glob(f"**/{pattern}"):
        path.unlink()


def _write_partitioned_outputs(
    dataframe: pd.DataFrame,
    *,
    source_month: MonthPartition,
) -> tuple[list[Path], list[dict[str, Any]]]:
    partitioned = dataframe.copy()
    partitioned["resolved_partition_year"] = (
        partitioned["pickup_year"].fillna(source_month.year).astype(int)
    )
    partitioned["resolved_partition_month"] = (
        partitioned["pickup_month"].fillna(source_month.month).astype(int)
    )

    output_files: list[Path] = []
    partition_details: list[dict[str, Any]] = []
    grouped = partitioned.groupby(
        ["resolved_partition_year", "resolved_partition_month"],
        dropna=False,
        sort=True,
    )

    for (partition_year, partition_month), partition_frame in grouped:
        output_path = build_silver_output_file_path(
            source_month=source_month,
            partition_year=int(partition_year),
            partition_month=int(partition_month),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned = partition_frame.drop(
            columns=["resolved_partition_year", "resolved_partition_month"],
        )
        cleaned.to_parquet(output_path, index=False)
        output_files.append(output_path)
        partition_details.append(
            {
                "pickup_year": int(partition_year),
                "pickup_month": int(partition_month),
                "row_count": int(len(cleaned)),
                "output_path": path_relative_to_project(output_path),
            }
        )

    return output_files, partition_details


def run_silver_pipeline(
    *,
    months: Sequence[MonthPartition] | None = None,
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Standardize monthly Yellow Taxi raw files into a partition-aware Silver table."""
    ensure_runtime_directories()
    settings = get_settings()
    selected_months = list(months or resolve_month_window(start_month=start_month, end_month=end_month))
    silver_state = read_state(settings.silver_state_path, "silver")
    months_to_process = select_months_to_process(selected_months, silver_state, force=force)
    months_to_process_keys = {month.month_id for month in months_to_process}

    results: list[dict[str, Any]] = []

    for month in selected_months:
        raw_path = build_bronze_raw_file_path(month)
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Raw Bronze file not found for {month.month_id}. Expected path: {raw_path}"
            )

        if month.month_id not in months_to_process_keys:
            existing_entry = get_month_entry(silver_state, month) or {}
            results.append(
                {
                    "source_month": month.month_id,
                    "status": "skipped",
                    "reason": "already_processed",
                    "metadata_path": existing_entry.get("metadata_path"),
                }
            )
            continue

        raw_dataframe = pd.read_parquet(raw_path)
        silver_dataframe = standardize_yellow_taxi_dataframe(
            raw_dataframe,
            source_month=month,
        )
        quality_report = build_silver_quality_report(
            raw_dataframe=raw_dataframe,
            silver_dataframe=silver_dataframe,
            source_month=month,
        )

        _clear_existing_month_outputs(month)
        output_files, partition_details = _write_partitioned_outputs(
            silver_dataframe,
            source_month=month,
        )

        metadata = build_silver_month_metadata(
            month_partition=month,
            output_files=output_files,
            partition_details=partition_details,
            quality_report=quality_report,
        )
        metadata_path = write_silver_month_metadata(metadata)

        silver_state = mark_month_completed(
            silver_state,
            month,
            {
                "metadata_path": path_relative_to_project(metadata_path),
                "output_files": metadata["output_files"],
                "row_count": quality_report["silver_row_count"],
                "row_count_preserved": quality_report["row_count_preserved"],
            },
        )
        results.append(
            {
                "source_month": month.month_id,
                "status": "processed",
                "metadata_path": path_relative_to_project(metadata_path),
                "output_file_count": len(output_files),
                "row_count": quality_report["silver_row_count"],
                "row_count_preserved": quality_report["row_count_preserved"],
            }
        )

    state_path = write_state(settings.silver_state_path, silver_state)
    run_metadata = build_silver_run_metadata(
        selected_months=[month.month_id for month in selected_months],
        results=results,
        force=force,
    )
    run_metadata["state_path"] = path_relative_to_project(state_path)
    run_metadata_path = write_silver_run_metadata(run_metadata)

    return {
        **run_metadata,
        "run_metadata_path": path_relative_to_project(run_metadata_path),
    }
