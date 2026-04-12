from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.bronze.pipeline import run_bronze_pipeline  # noqa: E402


def main() -> None:
    """Execute the local Bronze inventory and profiling job."""
    result = run_bronze_pipeline()
    profile = result["profiling_summary"]

    print("Bronze preparation completed.")
    print(f"Raw directory: {result['raw_directory']}")
    print(f"Discovered files: {result['file_count']}")
    print(f"Supported data files: {result['supported_data_file_count']}")
    print(f"Selected main file: {result['selected_main_file']}")
    print(f"Rows: {profile['row_count']}")
    print(f"Columns: {profile['column_count']}")
    print(f"Duplicate rows: {profile['duplicate_row_count']}")
    print(f"Metadata artifact: {result['metadata_path']}")


if __name__ == "__main__":
    main()
