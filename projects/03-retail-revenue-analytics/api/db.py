from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import duckdb

from config import ApiConfig
from serializers import serialize_rows


class DatabaseUnavailableError(RuntimeError):
    """Raised when the local DuckDB database file is unavailable."""


class DatabaseQueryError(RuntimeError):
    """Raised when the API cannot read from DuckDB marts."""


def ensure_database_exists(config: ApiConfig) -> None:
    """Raise if the expected local DuckDB file does not exist."""
    if not config.duckdb_path.exists():
        raise DatabaseUnavailableError(f"DuckDB file not found: {config.duckdb_path}")


def get_connection(config: ApiConfig) -> duckdb.DuckDBPyConnection:
    """Create a read-only DuckDB connection."""
    ensure_database_exists(config)
    return duckdb.connect(str(config.duckdb_path), read_only=True)


def check_database(config: ApiConfig) -> bool:
    """Run a lightweight DuckDB connectivity check."""
    try:
        with get_connection(config) as connection:
            row = connection.execute("select 1 as health_check").fetchone()
            return bool(row and row[0] == 1)
    except (duckdb.Error, OSError) as exc:
        raise DatabaseQueryError("Unable to connect to the DuckDB mart database.") from exc


def fetch_rows(
    config: ApiConfig,
    sql: str,
    parameters: Sequence[Any] | None = None,
) -> list[dict[str, Any]]:
    """Execute a read-only query and return JSON-friendly rows."""
    try:
        with get_connection(config) as connection:
            result = connection.execute(sql, parameters or [])
            columns = [description[0] for description in result.description]
            rows = [dict(zip(columns, row, strict=True)) for row in result.fetchall()]
            return serialize_rows(rows)
    except DatabaseUnavailableError:
        raise
    except duckdb.CatalogException as exc:
        raise DatabaseQueryError("A required DBT mart table is missing.") from exc
    except (duckdb.Error, OSError) as exc:
        raise DatabaseQueryError("Unable to query the DuckDB mart layer.") from exc
