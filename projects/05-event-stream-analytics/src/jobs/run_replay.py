from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.pipeline import run_gold_pipeline  # noqa: E402
from processing.silver.pipeline import run_silver_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the replay job."""
    parser = argparse.ArgumentParser(description="Replay downstream layers from landed Bronze raw files.")
    parser.add_argument(
        "--target",
        choices=("all", "silver", "gold"),
        default="all",
        help="Choose which downstream layer(s) to rebuild from local landed data.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the replay workflow."""
    args = parse_args()
    summary: dict[str, object] = {"job_name": "replay", "target": args.target}

    if args.target in ("all", "silver"):
        summary["silver"] = run_silver_pipeline(force=True)

    if args.target in ("all", "gold"):
        summary["gold"] = run_gold_pipeline(force=True)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
