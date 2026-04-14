from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.pipeline import run_gold_pipeline  # noqa: E402


def main() -> None:
    """Execute the local Gold v1 analytical summary job."""
    result = run_gold_pipeline()
    validation = result["validation_summary"]

    print("Gold preparation completed.")
    print(f"Source Silver dataset: {result['source_silver_dataset']}")

    for name, path in result["artifact_paths"].items():
        print(f"{name}: {path}")

    print("Output row counts:")
    for name, row_count in result["output_row_counts"].items():
        print(f"- {name}: {row_count}")

    print(f"Validation passed: {validation['is_valid']}")


if __name__ == "__main__":
    main()
