from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.bronze.pipeline import run_bronze_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Bronze consumer."""
    parser = argparse.ArgumentParser(description="Consume Redpanda events and land a raw Bronze batch.")
    parser.add_argument("--max-events", type=int, help="Maximum number of broker messages to land.")
    parser.add_argument("--max-seconds", type=int, help="Maximum run duration in seconds.")
    parser.add_argument(
        "--replay",
        action="store_true",
        help=(
            "Seek to the earliest retained broker offsets and land a new Bronze batch. "
            "Does NOT delete or replace previously landed Bronze files. "
            "Running this repeatedly over the same retained broker history creates multiple "
            "Bronze batches covering the same events, which will inflate Silver and Gold counts "
            "if downstream layers are rebuilt without clearing old outputs. "
            "Prefer run_replay.py to rebuild Silver and Gold from already-landed Bronze files."
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Execute the Bronze raw landing consumer."""
    args = parse_args()
    summary = run_bronze_pipeline(
        max_events=args.max_events,
        max_seconds=args.max_seconds,
        replay=args.replay,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
