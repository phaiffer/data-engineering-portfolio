from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import psycopg
from dotenv import load_dotenv
from psycopg import sql

from ingestion.raw_inventory import get_project_root, path_relative_to_project


SILVER_DATASET_PATH = get_project_root() / "data" / "silver" / "ai_job_market_insights_silver.csv"
DEFAULT_SCHEMA = "analytics"
DEFAULT_TABLE = "job_market_insights_silver"


@dataclass(frozen=True)
class PostgresLoadResult:
    source_file: str
    target_schema: str
    target_table: str
    rows_loaded: int


def load_project_env() -> None:
    """Load project-local PostgreSQL settings from .env when present."""
    load_dotenv(get_project_root() / ".env")


def get_postgres_connection_params() -> dict[str, Any]:
    """Return PostgreSQL connection parameters from project environment variables."""
    load_project_env()

    params = {
        "host": os.getenv("JOB_MARKET_POSTGRES_HOST", "localhost"),
        "port": int(os.getenv("JOB_MARKET_POSTGRES_PORT", "5432")),
        "dbname": os.getenv("JOB_MARKET_POSTGRES_DB", "job_market_analytics"),
        "user": os.getenv("JOB_MARKET_POSTGRES_USER", "postgres"),
        "password": os.getenv("JOB_MARKET_POSTGRES_PASSWORD", "postgres"),
    }
    return params


def load_silver_dataframe(silver_path: Path | None = None) -> pd.DataFrame:
    """Load the Silver artifact that will be copied into PostgreSQL."""
    path = silver_path or SILVER_DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Silver dataset was not found at {path}. Run run_silver.py first.")

    return pd.read_csv(path)


def recreate_silver_table(connection: psycopg.Connection, schema: str, table: str) -> None:
    """Create the target schema/table if needed and clear the table for a repeatable local load."""
    with connection.cursor() as cursor:
        cursor.execute(sql.SQL("create schema if not exists {}").format(sql.Identifier(schema)))
        cursor.execute(
            sql.SQL(
                """
                create table if not exists {}.{} (
                    job_title text not null,
                    industry text not null,
                    company_size text not null,
                    location text not null,
                    ai_adoption_level text not null,
                    automation_risk text not null,
                    required_skills text not null,
                    salary_usd double precision not null,
                    remote_friendly text not null,
                    job_growth_projection text not null
                )
                """
            ).format(sql.Identifier(schema), sql.Identifier(table))
        )
        cursor.execute(sql.SQL("truncate table {}.{}").format(sql.Identifier(schema), sql.Identifier(table)))


def insert_silver_dataframe(
    connection: psycopg.Connection,
    dataframe: pd.DataFrame,
    schema: str,
    table: str,
) -> int:
    """Insert Silver rows into the target PostgreSQL table."""
    columns = [
        "job_title",
        "industry",
        "company_size",
        "location",
        "ai_adoption_level",
        "automation_risk",
        "required_skills",
        "salary_usd",
        "remote_friendly",
        "job_growth_projection",
    ]
    missing_columns = [column for column in columns if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Silver dataset is missing expected columns: {missing_columns}")

    records = [tuple(row) for row in dataframe[columns].itertuples(index=False, name=None)]

    with connection.cursor() as cursor:
        cursor.executemany(
            sql.SQL(
                """
                insert into {}.{} (
                    job_title,
                    industry,
                    company_size,
                    location,
                    ai_adoption_level,
                    automation_risk,
                    required_skills,
                    salary_usd,
                    remote_friendly,
                    job_growth_projection
                )
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            ).format(sql.Identifier(schema), sql.Identifier(table)),
            records,
        )

    return len(records)


def load_silver_to_postgres(
    silver_path: Path | None = None,
    schema: str = DEFAULT_SCHEMA,
    table: str = DEFAULT_TABLE,
) -> PostgresLoadResult:
    """Load the local Silver artifact into PostgreSQL for DBT relational modeling."""
    source_path = silver_path or SILVER_DATASET_PATH
    dataframe = load_silver_dataframe(source_path)

    with psycopg.connect(**get_postgres_connection_params()) as connection:
        recreate_silver_table(connection, schema=schema, table=table)
        rows_loaded = insert_silver_dataframe(connection, dataframe=dataframe, schema=schema, table=table)
        connection.commit()

    return PostgresLoadResult(
        source_file=path_relative_to_project(source_path),
        target_schema=schema,
        target_table=table,
        rows_loaded=rows_loaded,
    )
