from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.append(str(SRC_ROOT))

from processing.silver.pipeline import run_silver_pipeline  # noqa: E402


def main() -> None:
    """Execute the Pandas-based Silver processing job."""
    result = run_silver_pipeline()
    validation_summary = result["validation_summary"]
    checks = validation_summary["checks"]

    print("Silver processing completed.")
    print(f"Input rows: {result['input_rows']}")
    print(f"Output rows: {result['output_rows']}")
    print(f"Output path: {result['output_path']}")
    print(f"Metadata path: {result['metadata_path']}")
    print(f"Columns written: {', '.join(result['columns'])}")
    print(f"Duplicate rows: {result['duplicate_rows']}")
    print(f"Validation passed: {validation_summary['passed']}")
    print(f"Key null counts: {checks['key_null_counts']}")
    print(f"Numeric conversion summary: {checks['numeric_conversions']}")


if __name__ == "__main__":
    main()
