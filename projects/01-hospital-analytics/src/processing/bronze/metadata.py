from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingestion.raw_inventory import (
    DATASET_HANDLE,
    get_bronze_metadata_dir,
    path_relative_to_project,
)


BRONZE_SCOPE_NOTES = [
    "Initial Bronze phase only: raw file inventory, raw metadata capture, and CSV profiling.",
    "No Silver transformations are applied in this step.",
    "Raw column names, values, duplicate rows, and nulls are preserved.",
    "Pandas is used temporarily for local profiling because local PySpark is blocked.",
]


def build_bronze_metadata(
    *,
    raw_inventory: dict[str, Any],
    selected_main_file: Path,
    profiling_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build the serializable Bronze metadata document."""
    return {
        "dataset_handle": DATASET_HANDLE,
        "local_raw_directory": raw_inventory["raw_directory"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "discovered_files": raw_inventory,
        "selected_main_file": path_relative_to_project(selected_main_file),
        "main_file_selection_rule": "largest CSV file by size, with path-based tie breaking",
        "profiling_summary": profiling_summary,
        "bronze_scope_notes": BRONZE_SCOPE_NOTES,
    }


def write_bronze_metadata(
    metadata: dict[str, Any],
    output_dir: Path | None = None,
    filename: str = "healthcare_analytics_patient_flow_bronze_metadata.json",
) -> Path:
    """Write the Bronze metadata document to a readable JSON artifact."""
    target_dir = output_dir or get_bronze_metadata_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / filename
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path
