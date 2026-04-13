from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from serving.postgres_loader import run_serving_load  # noqa: E402


def main() -> None:
    """Load Gold outputs into PostgreSQL and create serving views."""
    result = run_serving_load()

    print("Serving load completed.")
    print(f"Analytics schema: {result['analytics_schema']}")
    print(f"Serving schema: {result['serving_schema']}")
    print("Tables loaded:")
    for dataset_name, table_info in result["loaded_tables"].items():
        print(
            f"- {table_info['schema']}.{table_info['table']}: "
            f"{table_info['row_count']} rows from {dataset_name}"
        )
    print("Views created:")
    for view_name in result["created_views"]:
        print(f"- {result['serving_schema']}.{view_name}")


if __name__ == "__main__":
    main()
