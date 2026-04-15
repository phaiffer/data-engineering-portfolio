from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.pipeline import run_gold_pipeline  # noqa: E402


def main() -> None:
    """Execute the local Gold v1 analytical output job."""
    result = run_gold_pipeline()

    print("Gold preparation completed.")
    print(f"Outputs written: {result['output_count']}")
    for output in result["outputs"]:
        print(
            f"- {output['output_file']}: "
            f"{output['row_count']} rows, {output['column_count']} columns"
        )
    print(f"Run metadata artifact: {result['metadata_path']}")


if __name__ == "__main__":
    main()
