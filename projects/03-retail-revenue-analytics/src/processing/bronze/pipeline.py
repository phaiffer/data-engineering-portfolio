from __future__ import annotations

from pathlib import Path
from typing import Any

from ingestion.raw_inventory import (
    discover_raw_files,
    get_raw_data_dir,
    list_supported_data_files,
    path_relative_to_project,
)
from processing.bronze.metadata import build_bronze_metadata, write_bronze_metadata
from processing.bronze.profiling import profile_csv_file, select_main_csv_file


def run_bronze_pipeline(raw_data_dir: Path | None = None) -> dict[str, Any]:
    """
    Run the initial Bronze foundation job.

    This job inventories the raw landing directory, selects the largest
    supported CSV for first-pass profiling, profiles it with Pandas, and writes
    a JSON metadata artifact.
    """
    raw_dir = raw_data_dir or get_raw_data_dir()
    raw_inventory = discover_raw_files(raw_dir)
    csv_files = list_supported_data_files(raw_dir)
    selected_main_file = select_main_csv_file(csv_files)
    profiling_summary = profile_csv_file(selected_main_file)
    metadata = build_bronze_metadata(
        raw_inventory=raw_inventory,
        selected_main_file=selected_main_file,
        profiling_summary=profiling_summary,
    )
    metadata_path = write_bronze_metadata(metadata)

    return {
        "raw_directory": path_relative_to_project(raw_dir),
        "metadata_path": path_relative_to_project(metadata_path),
        "selected_main_file": path_relative_to_project(selected_main_file),
        "file_count": raw_inventory["file_count"],
        "supported_data_file_count": raw_inventory["supported_data_file_count"],
        "profiling_summary": profiling_summary,
    }
