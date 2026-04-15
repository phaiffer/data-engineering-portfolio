from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from orchestration.flows import run_urban_mobility_flow  # noqa: E402


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the Prefect flow entrypoint."""
    parser = argparse.ArgumentParser(description="Run the urban mobility Prefect flow locally.")
    parser.add_argument("--start-month", help="Inclusive month bound in YYYY-MM format.")
    parser.add_argument("--end-month", help="Inclusive month bound in YYYY-MM format.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force all selected months through each layer.",
    )
    return parser.parse_args()


def main() -> None:
    """Execute the local Prefect flow."""
    args = parse_args()
    summary = run_urban_mobility_flow(
        start_month=args.start_month,
        end_month=args.end_month,
        force=args.force,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
