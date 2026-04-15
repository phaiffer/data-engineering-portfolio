from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.silver.pipeline import run_silver_pipeline  # noqa: E402


def main() -> None:
    """Execute the local source-aligned Silver standardization job."""
    result = run_silver_pipeline()

    print("Silver preparation completed.")
    print(f"Tables written: {result['table_count']}")
    for table in result["tables"]:
        print(
            f"- {table['logical_table_name']}: "
            f"{table['row_count']} rows, {table['column_count']} columns -> {table['output_file']}"
        )
    print(f"Run metadata artifact: {result['metadata_path']}")


if __name__ == "__main__":
    main()
