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


MART_COLUMNS: dict[str, tuple[str, ...]] = {
    "mart_job_title_summary": (
        "job_title",
        "total_records",
        "average_salary_usd",
        "median_salary_usd",
        "min_salary_usd",
        "max_salary_usd",
        "remote_friendly_share",
        "high_automation_risk_share",
        "high_ai_adoption_share",
        "growth_projection_share",
    ),
    "mart_industry_summary": (
        "industry",
        "total_records",
        "average_salary_usd",
        "median_salary_usd",
        "min_salary_usd",
        "max_salary_usd",
        "remote_friendly_share",
        "high_automation_risk_share",
        "high_ai_adoption_share",
        "growth_projection_share",
    ),
    "mart_location_summary": (
        "location",
        "total_records",
        "average_salary_usd",
        "median_salary_usd",
        "min_salary_usd",
        "max_salary_usd",
        "remote_friendly_share",
        "high_automation_risk_share",
        "high_ai_adoption_share",
        "growth_projection_share",
    ),
    "mart_automation_ai_summary": (
        "automation_risk",
        "ai_adoption_level",
        "total_records",
        "average_salary_usd",
        "median_salary_usd",
        "remote_friendly_share",
        "growth_projection_share",
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


def check_database_connection(config: ApiConfig) -> bool:
    """Run a lightweight PostgreSQL connectivity check."""
    try:
        with get_connection(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select 1 as health_check")
                row = cursor.fetchone()
                return bool(row and row["health_check"] == 1)
    except psycopg.Error as exc:
        raise DatabaseQueryError("Unable to connect to PostgreSQL.") from exc


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


def fetch_dashboard_kpis(config: ApiConfig) -> dict[str, Any]:
    """Fetch whole-dataset KPIs from the PostgreSQL Silver table."""
    statement = sql.SQL(
        """
        select
            count(*) as total_records,
            avg(salary_usd) as average_salary_usd,
            percentile_cont(0.5) within group (order by salary_usd) as median_salary_usd,
            avg(case when lower(remote_friendly) = 'yes' then 1.0 else 0.0 end) as remote_friendly_share,
            avg(case when lower(ai_adoption_level) = 'high' then 1.0 else 0.0 end) as high_ai_adoption_share,
            avg(case when lower(automation_risk) = 'high' then 1.0 else 0.0 end) as high_automation_risk_share,
            avg(case when lower(job_growth_projection) = 'growth' then 1.0 else 0.0 end) as growth_projection_share
        from {}.{}
        """
    ).format(sql.Identifier(config.silver_schema), sql.Identifier(config.silver_table))

    try:
        with get_connection(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
                row = cursor.fetchone()
                return normalize_row(row) if row else {}
    except psycopg.Error as exc:
        raise DatabaseQueryError("Unable to query the PostgreSQL Silver layer.") from exc


def build_mart_select_statement(
    config: ApiConfig,
    mart_name: str,
    order_by: str | None = None,
    limit: int | None = None,
    descending: bool = True,
) -> sql.Composed:
    """Build a safe SELECT statement for one whitelisted mart."""
    if mart_name not in MART_COLUMNS:
        raise ValueError(f"Unknown mart: {mart_name}")
    if order_by is not None and order_by not in MART_COLUMNS[mart_name]:
        raise ValueError(f"Unsupported order_by column for {mart_name}: {order_by}")

    selected_columns = sql.SQL(", ").join(
        sql.Identifier(column_name) for column_name in MART_COLUMNS[mart_name]
    )

    statement = sql.SQL("select {} from {}.{}").format(
        selected_columns,
        sql.Identifier(config.marts_schema),
        sql.Identifier(mart_name),
    )

    if order_by is not None:
        direction = sql.SQL(" desc") if descending else sql.SQL(" asc")
        statement += sql.SQL(" order by {}").format(sql.Identifier(order_by)) + direction
    if limit is not None:
        statement += sql.SQL(" limit {}").format(sql.Literal(limit))

    return statement


def fetch_mart_rows(
    config: ApiConfig,
    mart_name: str,
    order_by: str | None = None,
    limit: int | None = None,
    descending: bool = True,
) -> list[dict[str, Any]]:
    """Fetch rows from a PostgreSQL DBT mart."""
    try:
        statement = build_mart_select_statement(
            config=config,
            mart_name=mart_name,
            order_by=order_by,
            limit=limit,
            descending=descending,
        )
        with get_connection(config) as connection:
            with connection.cursor() as cursor:
                cursor.execute(statement)
                return [normalize_row(row) for row in cursor.fetchall()]
    except psycopg.Error as exc:
        raise DatabaseQueryError("Unable to query the PostgreSQL mart layer.") from exc
