from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import path_relative_to_project


def select_main_csv_file(csv_files: list[Path]) -> Path:
    """
    Select the main CSV file for initial Bronze profiling.

    Rule: choose the largest CSV by file size, then by path for deterministic ties.
    This is intentionally simple and explainable for raw landing inventory work:
    when Kaggle datasets contain multiple CSVs, the largest file is usually the
    primary fact-like extract, while smaller files are often references or samples.
    """
    if not csv_files:
        raise FileNotFoundError("No CSV files were found for Bronze profiling.")

    return sorted(csv_files, key=lambda path: (-path.stat().st_size, path.as_posix()))[0]


def profile_csv_file(csv_path: Path) -> dict[str, Any]:
    """
    Profile a raw CSV file without changing columns, values, or record-level content.

    Pandas is used as a temporary local profiling engine while Spark setup is blocked.
    The returned dictionary is intentionally engine-neutral so the implementation can
    migrate to PySpark later with minimal changes to job orchestration and metadata.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file does not exist: {csv_path}")

    dataframe = pd.read_csv(csv_path)

    return {
        "file": path_relative_to_project(csv_path),
        "engine": "pandas",
        "row_count": int(len(dataframe)),
        "column_count": int(len(dataframe.columns)),
        "column_names": list(dataframe.columns),
        "inferred_dtypes": {column: str(dtype) for column, dtype in dataframe.dtypes.items()},
        "null_counts": {column: int(count) for column, count in dataframe.isna().sum().items()},
        "duplicate_row_count": int(dataframe.duplicated().sum()),
    }
