from __future__ import annotations

from typing import Any

import pandas as pd

from ingestion.raw_inventory import path_relative_to_project
from processing.silver.config import (
    discover_source_registry,
    get_config_by_logical_name,
    get_silver_tables_dir,
    get_silver_v1_configs,
)
from processing.silver.metadata import (
    build_run_metadata,
    build_table_metadata,
    write_run_metadata,
    write_table_metadata,
)
from processing.silver.standardization import standardize_source_table


def run_silver_pipeline() -> dict[str, Any]:
    """
    Run source-aligned Silver standardization for selected Olist tables.

    Each output table preserves its source row grain. No business joins,
    aggregations, surrogate keys, or dimensional modeling are applied.
    """
    registry = discover_source_registry()
    expected_configs = get_silver_v1_configs()
    missing_tables = [
        config.logical_name for config in expected_configs if config.logical_name not in registry
    ]
    if missing_tables:
        missing_list = ", ".join(sorted(missing_tables))
        raise FileNotFoundError(f"Missing raw source files for Silver tables: {missing_list}")

    tables_dir = get_silver_tables_dir()
    tables_dir.mkdir(parents=True, exist_ok=True)

    table_results: list[dict[str, Any]] = []

    for config in expected_configs:
        raw_source_file = registry[config.logical_name]
        dataframe = pd.read_csv(raw_source_file)
        silver_dataframe = standardize_source_table(
            dataframe,
            datetime_columns=config.datetime_columns,
            numeric_columns=config.numeric_columns,
        )

        output_file = tables_dir / f"{config.logical_name}.csv"
        silver_dataframe.to_csv(output_file, index=False)

        table_metadata = build_table_metadata(
            logical_table_name=config.logical_name,
            raw_source_file=raw_source_file,
            output_file=output_file,
            dataframe=silver_dataframe,
            config_notes=config.notes,
        )
        metadata_path = write_table_metadata(table_metadata)

        table_results.append(
            {
                "logical_table_name": config.logical_name,
                "raw_source_file": path_relative_to_project(raw_source_file),
                "output_file": path_relative_to_project(output_file),
                "metadata_file": path_relative_to_project(metadata_path),
                "row_count": table_metadata["row_count"],
                "column_count": table_metadata["column_count"],
                "duplicate_row_count": table_metadata["duplicate_row_count"],
            }
        )

    run_metadata = build_run_metadata(table_results)
    run_metadata_path = write_run_metadata(run_metadata)

    return {
        "table_count": len(table_results),
        "tables": table_results,
        "metadata_path": path_relative_to_project(run_metadata_path),
    }
