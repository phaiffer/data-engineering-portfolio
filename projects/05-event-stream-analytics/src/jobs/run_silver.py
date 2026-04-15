from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.silver.pipeline import run_silver_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Silver job."""
    parser = argparse.ArgumentParser(description="Standardize landed Bronze event batches into Silver Parquet.")
    parser.add_argument(
        "--batch-id",
        action="append",
        help="Optional Bronze batch id to process. Repeat the flag for multiple batch ids.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild Silver outputs for the selected Bronze batches.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the Silver standardization job."""
    args = parse_args()
    summary = run_silver_pipeline(
        batch_ids=args.batch_id,
        force=args.force,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
