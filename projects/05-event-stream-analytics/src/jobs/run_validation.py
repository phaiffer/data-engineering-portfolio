from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from operations.validation import write_validation_manifest  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the local validation manifest."""
    parser = argparse.ArgumentParser(description="Build a local validation manifest from runtime artifacts.")
    parser.add_argument(
        "--mode",
        choices=("normal", "broker_replay", "offline_replay"),
        default="normal",
        help="Label the validation context without changing any pipeline data.",
    )
    return parser.parse_args()


def main() -> None:
    """Build and print the local validation manifest."""
    args = parse_args()
    summary = write_validation_manifest(mode=args.mode)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
