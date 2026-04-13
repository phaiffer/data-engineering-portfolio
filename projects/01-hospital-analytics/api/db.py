from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from config import ApiConfig


class DatabaseQueryError(RuntimeError):
    """Raised when the API cannot read from PostgreSQL."""


VIEW_COLUMNS: dict[str, tuple[str, ...]] = {
    "v_daily_patient_flow": (
        "admission_date",
        "total_patient_events",
        "average_patient_waittime",
        "average_patient_satisfaction_score",
        "admitted_patient_events",
        "null_department_referral_events",
        "null_satisfaction_score_events",
    ),
    "v_department_referral_summary": (
        "department_referral",
        "total_patient_events",
        "average_patient_waittime",
        "average_patient_satisfaction_score",
        "share_of_total_events",
    ),
    "v_demographic_summary": (
        "patient_gender",
        "patient_race",
        "patient_age_band",
        "total_patient_events",
        "average_patient_waittime",
        "average_patient_satisfaction_score",
    ),
    "v_dashboard_kpis": (
        "total_patient_events",
        "average_waittime_overall",
        "average_satisfaction_overall",
        "number_of_daily_points",
        "number_of_department_groups",
        "number_of_demographic_groups",
    ),
}


def get_connection(config: ApiConfig) -> psycopg.Connection:
    """Create a PostgreSQL connection using the project .env settings."""
    return psycopg.connect(
        host=config.postgres_host,
        port=config.postgres_port,
        dbname=config.postgres_db,
        user=config.postgres_user,
        password=config.postgres_password,
        row_factory=dict_row,
    )


def normalize_value(value: Any) -> Any:
    """Convert PostgreSQL values into JSON-friendly Python values."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert one database row into a JSON-friendly dictionary."""
    return {key: normalize_value(value) for key, value in row.items()}


def build_select_statement(
    config: ApiConfig,
    view_name: str,
    order_by: str | None = None,
    limit: int | None = None,
) -> sql.Composed:
    """Build a safe SELECT statement for one whitelisted serving view."""
    if view_name not in VIEW_COLUMNS:
        raise ValueError(f"Unknown serving view: {view_name}")
    if order_by is not None and order_by not in VIEW_COLUMNS[view_name]:
        raise ValueError(f"Unsupported order_by column for {view_name}: {order_by}")

    statement = sql.SQL("SELECT * FROM {}.{}").format(
        sql.Identifier(config.serving_schema),
        sql.Identifier(view_name),
    )

    if order_by is not None:
        statement += sql.SQL(" ORDER BY {}").format(sql.Identifier(order_by))
    if limit is not None:
        statement += sql.SQL(" LIMIT {}").format(sql.Literal(limit))

    return statement


def fetch_rows(
    config: ApiConfig,
    view_name: str,
    order_by: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch rows from a PostgreSQL serving view."""
    try:
        statement = build_select_statement(config, view_name, order_by, limit)
        with get_connection(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
                return [normalize_row(row) for row in cursor.fetchall()]
    except psycopg.Error as exc:
        raise DatabaseQueryError("Unable to query the PostgreSQL serving layer.") from exc


def fetch_one(config: ApiConfig, view_name: str) -> dict[str, Any] | None:
    """Fetch a single row from a PostgreSQL serving view."""
    rows = fetch_rows(config=config, view_name=view_name, limit=1)
    return rows[0] if rows else None
