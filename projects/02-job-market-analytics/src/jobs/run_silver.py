from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.silver.pipeline import run_silver_pipeline  # noqa: E402


def main() -> None:
    """Execute the local Silver v1 standardization job."""
    result = run_silver_pipeline()
    validation = result["validation_summary"]
    numeric_summary = validation["numeric_summary"].get("salary_usd", {})

    print("Silver preparation completed.")
    print(f"Source file: {result['source_file']}")
    print(f"Silver dataset: {result['dataset_path']}")
    print(f"Silver metadata: {result['metadata_path']}")
    print(f"Raw rows: {validation['raw_row_count']}")
    print(f"Silver rows: {validation['silver_row_count']}")
    print(f"Row count preserved: {validation['row_count_preserved']}")
    print(f"Duplicate rows: {validation['duplicate_row_count']}")
    print(f"Missing expected columns: {validation['missing_columns']}")
    print(f"Null-heavy columns: {validation['null_heavy_columns']}")
    print(f"Salary USD min: {numeric_summary.get('min')}")
    print(f"Salary USD max: {numeric_summary.get('max')}")
    print(f"Validation passed: {validation['is_valid']}")


if __name__ == "__main__":
    main()
