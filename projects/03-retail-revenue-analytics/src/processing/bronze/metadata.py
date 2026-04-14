from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingestion.raw_inventory import (
    DATASET_HANDLE,
    DATASET_FOLDER_NAME,
    get_bronze_metadata_dir,
    path_relative_to_project,
)


BRONZE_SCOPE_NOTES = [
    "Initial Bronze foundation only: raw file inventory, source metadata capture, and CSV profiling.",
    "Bronze keeps raw files unchanged and does not apply business transformations.",
    "No columns are renamed, business types are cast, rows are deduplicated, records are filtered, or metrics are aggregated.",
    "Fact and dimension semantics are intentionally deferred until Silver and dimensional modeling work is designed from the source relationships.",
    "The largest-CSV selection is a raw-stage profiling rule only, not a final analytical fact-grain decision.",
]

SOURCE_NOTES = [
    "Dataset is sourced from Kaggle through kagglehub.",
    "The analytical domain is retail and e-commerce revenue analytics.",
    "Olist contains multiple related raw CSV files, including orders, order items, payments, products, customers, sellers, reviews, and geolocation.",
    "Future revenue KPI and dimensional modeling decisions should use the relationships across these files, not the Bronze profiling selection alone.",
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
        "main_file_selection_rule": "largest CSV file by size, with path-based tie breaking; raw-stage profiling rule only",
        "profiling_summary": profiling_summary,
        "source_notes": SOURCE_NOTES,
        "bronze_scope_notes": BRONZE_SCOPE_NOTES,
    }


def write_bronze_metadata(
    metadata: dict[str, Any],
    output_dir: Path | None = None,
    filename: str = f"{DATASET_FOLDER_NAME}_bronze_metadata.json",
) -> Path:
    """Write the Bronze metadata document to a readable JSON artifact."""
    target_dir = output_dir or get_bronze_metadata_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / filename
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path
