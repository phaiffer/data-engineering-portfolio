from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from serving.postgres_loader import DEFAULT_SCHEMA, DEFAULT_TABLE, load_silver_to_postgres


def main() -> int:
    """Load the Silver artifact into PostgreSQL for DBT relational modeling."""
    result = load_silver_to_postgres(schema=DEFAULT_SCHEMA, table=DEFAULT_TABLE)

    print("PostgreSQL Silver load complete")
    print(f"Source file: {result.source_file}")
    print(f"Target table: {result.target_schema}.{result.target_table}")
    print(f"Rows loaded: {result.rows_loaded}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
