from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.pipeline import run_gold_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Gold job."""
    parser = argparse.ArgumentParser(description="Build Gold streaming summaries from Silver event data.")
    parser.add_argument(
        "--event-date",
        action="append",
        help="Optional event date to rebuild in YYYY-MM-DD format. Repeat the flag for multiple dates.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild Gold outputs for the selected event dates.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the Gold summary job."""
    args = parse_args()
    summary = run_gold_pipeline(
        event_dates=args.event_date,
        force=args.force,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
