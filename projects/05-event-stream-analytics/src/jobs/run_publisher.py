from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from stream.publisher import run_publisher  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the live stream publisher."""
    parser = argparse.ArgumentParser(description="Publish a bounded Wikimedia RecentChange sample to Redpanda.")
    parser.add_argument("--max-events", type=int, help="Maximum number of published non-canary events.")
    parser.add_argument("--max-seconds", type=int, help="Maximum run duration in seconds.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore the saved publisher checkpoint and start from the current live stream position.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the bounded publisher."""
    args = parse_args()
    summary = run_publisher(
        max_events=args.max_events,
        max_seconds=args.max_seconds,
        force=args.force,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
