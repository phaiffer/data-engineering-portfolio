from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq

from config import MonthPartition, get_settings, path_relative_to_project
from ingestion.state import build_run_metadata_summary


TEMPORAL_COLUMNS = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]


def _get_temporal_bounds(raw_path: Path) -> dict[str, dict[str, str | None]]:
    available_columns = []
    parquet_file = pq.ParquetFile(raw_path)
    for column in TEMPORAL_COLUMNS:
        if column in parquet_file.schema_arrow.names:
            available_columns.append(column)

    if not available_columns:
        return {}

    temporal_frame = pd.read_parquet(raw_path, columns=available_columns)
    bounds: dict[str, dict[str, str | None]] = {}

    for column in available_columns:
        series = pd.to_datetime(temporal_frame[column], errors="coerce")
        non_null = series.dropna()
        bounds[column] = {
            "min": None if non_null.empty else non_null.min().isoformat(),
            "max": None if non_null.empty else non_null.max().isoformat(),
        }

    return bounds


def build_bronze_month_metadata(
    *,
    month_partition: MonthPartition,
    raw_path: Path,
    ingestion_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build metadata for one landed raw month."""
    parquet_file = pq.ParquetFile(raw_path)
    arrow_schema = parquet_file.schema_arrow

    return {
        "source_month": month_partition.month_id,
        "raw_path": path_relative_to_project(raw_path),
        "file_size_bytes": int(raw_path.stat().st_size),
        "row_count": int(parquet_file.metadata.num_rows),
        "row_group_count": int(parquet_file.num_row_groups),
        "column_count": len(arrow_schema.names),
        "columns": arrow_schema.names,
        "column_types": {field.name: str(field.type) for field in arrow_schema},
        "temporal_bounds": _get_temporal_bounds(raw_path),
        "ingestion_state": ingestion_entry or {},
    }


def write_bronze_month_metadata(metadata: dict[str, Any]) -> Path:
    """Write one month-level Bronze metadata file."""
    settings = get_settings()
    output_path = settings.bronze_metadata_dir / f"bronze_month_{metadata['source_month']}.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def build_bronze_run_metadata(
    *,
    selected_months: list[str],
    results: list[dict[str, Any]],
    force: bool,
    run_started_at_utc: str,
) -> dict[str, Any]:
    """Build a compact run-level Bronze metadata summary."""
    metadata = build_run_metadata_summary(
        layer="bronze_metadata",
        selected_months=selected_months,
        results=results,
        force=force,
        run_started_at_utc=run_started_at_utc,
        processed_statuses={"profiled"},
    )
    metadata["profiled_month_count"] = metadata["processed_month_count"]
    return metadata


def write_bronze_run_metadata(metadata: dict[str, Any]) -> Path:
    """Write the latest Bronze run summary."""
    settings = get_settings()
    output_path = settings.bronze_metadata_dir / "latest_bronze_run.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path
