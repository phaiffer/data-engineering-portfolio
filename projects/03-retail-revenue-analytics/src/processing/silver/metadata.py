from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import DATASET_HANDLE, path_relative_to_project
from processing.silver.config import get_silver_metadata_dir


SILVER_SCOPE_NOTES = [
    "Silver v1 is source-aligned and preserves the row grain of each selected raw table.",
    "Safe standardization includes column-name normalization, whitespace trimming, blank-string null handling, and configured datetime/numeric parsing.",
    "Silver v1 does not aggregate, deduplicate, create surrogate keys, or join all sources into one canonical table.",
    "Dimensional modeling decisions are deferred to later modeled marts after source relationships are reviewed.",
]


def build_table_metadata(
    *,
    logical_table_name: str,
    raw_source_file: Path,
    output_file: Path,
    dataframe: pd.DataFrame,
    config_notes: str,
) -> dict[str, Any]:
    """Build metadata for one Silver table artifact."""
    return {
        "dataset_handle": DATASET_HANDLE,
        "logical_table_name": logical_table_name,
        "raw_source_file": path_relative_to_project(raw_source_file),
        "output_file": path_relative_to_project(output_file),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "column_names": list(dataframe.columns),
        "dtypes": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
        "null_counts": {column: int(count) for column, count in dataframe.isna().sum().items()},
        "duplicate_row_count": int(dataframe.duplicated().sum()),
        "table_notes": [config_notes],
        "silver_scope_notes": SILVER_SCOPE_NOTES,
    }


def write_table_metadata(metadata: dict[str, Any], output_dir: Path | None = None) -> Path:
    """Write metadata for one Silver table artifact."""
    target_dir = output_dir or get_silver_metadata_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / f"{metadata['logical_table_name']}_silver_metadata.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def build_run_metadata(table_results: list[dict[str, Any]]) -> dict[str, Any]:
    """Build run-level metadata for the Silver execution."""
    return {
        "dataset_handle": DATASET_HANDLE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "layer": "silver",
        "table_count": len(table_results),
        "tables": table_results,
        "scope_notes": SILVER_SCOPE_NOTES,
    }


def write_run_metadata(metadata: dict[str, Any], output_dir: Path | None = None) -> Path:
    """Write run-level Silver metadata."""
    target_dir = output_dir or get_silver_metadata_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / "silver_run_summary.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path
