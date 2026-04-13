from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.pipeline import run_gold_pipeline  # noqa: E402


def main() -> None:
    """Execute the local Pandas-based Gold processing job."""
    result = run_gold_pipeline()

    print("Gold processing completed.")
    print(f"Source path: {result['source_path']}")
    print(f"Source rows: {result['source_validation']['source_row_count']}")
    for name, output in result["outputs"].items():
        print(f"{name}: {output['row_count']} rows -> {output['path']}")
    print(f"Metadata path: {result['metadata_path']}")
    print(f"Validation passed: {result['validation_summary']['passed']}")


if __name__ == "__main__":
    main()
