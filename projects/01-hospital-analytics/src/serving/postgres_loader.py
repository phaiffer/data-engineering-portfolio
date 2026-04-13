from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from pandas.api import types as pd_types
from psycopg import sql

from processing.gold.pipeline import get_default_gold_output_paths
from utils.postgres import get_postgres_connection


ANALYTICS_SCHEMA = "analytics"
SERVING_SCHEMA = "serving"


@dataclass(frozen=True)
class GoldTableConfig:
    """Configuration for loading one Gold CSV artifact into PostgreSQL."""

    dataset_name: str
    table_name: str
    csv_path: Path
    date_columns: tuple[str, ...] = ()


def get_gold_table_configs(
    gold_paths: dict[str, Path] | None = None,
) -> list[GoldTableConfig]:
    """Return the Gold CSV to PostgreSQL table mapping."""
    paths = gold_paths or get_default_gold_output_paths()
    return [
        GoldTableConfig(
            dataset_name="daily_patient_flow",
            table_name="daily_patient_flow",
            csv_path=paths["daily_patient_flow"],
            date_columns=("admission_date",),
        ),
        GoldTableConfig(
            dataset_name="department_referral_summary",
            table_name="department_referral_summary",
            csv_path=paths["department_referral_summary"],
        ),
        GoldTableConfig(
            dataset_name="demographic_summary",
            table_name="demographic_summary",
            csv_path=paths["demographic_summary"],
        ),
    ]


def load_gold_csv(config: GoldTableConfig) -> pd.DataFrame:
    """Read and lightly type one Gold CSV artifact."""
    if not config.csv_path.exists():
        raise FileNotFoundError(f"Gold CSV file does not exist: {config.csv_path}")

    dataframe = pd.read_csv(config.csv_path)
    if dataframe.empty:
        raise ValueError(f"Gold CSV file is empty: {config.csv_path}")

    for column in config.date_columns:
        if column not in dataframe.columns:
            raise ValueError(
                f"Expected date column '{column}' in Gold CSV: {config.csv_path}"
            )
        dataframe[column] = pd.to_datetime(dataframe[column], errors="raise").dt.date

    return dataframe


def infer_postgres_type(series: pd.Series, force_date: bool = False) -> str:
    """Infer a practical PostgreSQL type from a Pandas series."""
    if force_date:
        return "DATE"
    if pd_types.is_integer_dtype(series):
        return "BIGINT"
    if pd_types.is_float_dtype(series):
        return "DOUBLE PRECISION"
    if pd_types.is_bool_dtype(series):
        return "BOOLEAN"
    if pd_types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"
    return "TEXT"


def build_create_table_sql(
    dataframe: pd.DataFrame,
    schema_name: str,
    table_name: str,
    date_columns: tuple[str, ...] = (),
) -> sql.Composed:
    """Build a CREATE TABLE statement from a DataFrame schema."""
    column_definitions = [
        sql.SQL("{} {}").format(
            sql.Identifier(column),
            sql.SQL(
                infer_postgres_type(
                    dataframe[column],
                    force_date=column in date_columns,
                )
            ),
        )
        for column in dataframe.columns
    ]

    return sql.SQL("CREATE TABLE IF NOT EXISTS {}.{} ({});").format(
        sql.Identifier(schema_name),
        sql.Identifier(table_name),
        sql.SQL(", ").join(column_definitions),
    )


def normalize_copy_value(value: Any) -> Any:
    """Convert Pandas missing values into PostgreSQL NULL values."""
    if pd.isna(value):
        return None
    return value


def copy_dataframe_to_table(
    dataframe: pd.DataFrame,
    schema_name: str,
    table_name: str,
    connection,
) -> int:
    """Replace table contents and load a DataFrame with PostgreSQL COPY."""
    columns = list(dataframe.columns)
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("TRUNCATE TABLE {}.{};").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )
        copy_sql = sql.SQL("COPY {}.{} ({}) FROM STDIN").format(
            sql.Identifier(schema_name),
            sql.Identifier(table_name),
            sql.SQL(", ").join(sql.Identifier(column) for column in columns),
        )
        with cursor.copy(copy_sql) as copy:
            for row in dataframe.itertuples(index=False, name=None):
                copy.write_row([normalize_copy_value(value) for value in row])

        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}.{};").format(
                sql.Identifier(schema_name),
                sql.Identifier(table_name),
            )
        )
        row_count = cursor.fetchone()[0]

    if row_count != len(dataframe):
        raise ValueError(
            f"Loaded row count mismatch for {schema_name}.{table_name}: "
            f"PostgreSQL={row_count}, CSV={len(dataframe)}"
        )

    return int(row_count)


def load_gold_tables(
    configs: list[GoldTableConfig] | None = None,
    analytics_schema: str = ANALYTICS_SCHEMA,
) -> dict[str, Any]:
    """Load all configured Gold CSV artifacts into PostgreSQL analytics tables."""
    table_configs = configs or get_gold_table_configs()
    loaded_tables: dict[str, Any] = {}

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                    sql.Identifier(analytics_schema)
                )
            )

        for config in table_configs:
            dataframe = load_gold_csv(config)
            with connection.cursor() as cursor:
                cursor.execute(
                    build_create_table_sql(
                        dataframe=dataframe,
                        schema_name=analytics_schema,
                        table_name=config.table_name,
                        date_columns=config.date_columns,
                    )
                )

            row_count = copy_dataframe_to_table(
                dataframe=dataframe,
                schema_name=analytics_schema,
                table_name=config.table_name,
                connection=connection,
            )
            loaded_tables[config.dataset_name] = {
                "schema": analytics_schema,
                "table": config.table_name,
                "csv_path": str(config.csv_path),
                "row_count": row_count,
                "columns": list(dataframe.columns),
            }

    return loaded_tables


def create_serving_views(
    analytics_schema: str = ANALYTICS_SCHEMA,
    serving_schema: str = SERVING_SCHEMA,
) -> list[str]:
    """Create or replace lightweight serving views for API and dashboard use."""
    view_statements = [
        (
            "v_daily_patient_flow",
            sql.SQL(
                """
                CREATE OR REPLACE VIEW {}.{} AS
                SELECT *
                FROM {}.{};
                """
            ).format(
                sql.Identifier(serving_schema),
                sql.Identifier("v_daily_patient_flow"),
                sql.Identifier(analytics_schema),
                sql.Identifier("daily_patient_flow"),
            ),
        ),
        (
            "v_department_referral_summary",
            sql.SQL(
                """
                CREATE OR REPLACE VIEW {}.{} AS
                SELECT *
                FROM {}.{};
                """
            ).format(
                sql.Identifier(serving_schema),
                sql.Identifier("v_department_referral_summary"),
                sql.Identifier(analytics_schema),
                sql.Identifier("department_referral_summary"),
            ),
        ),
        (
            "v_demographic_summary",
            sql.SQL(
                """
                CREATE OR REPLACE VIEW {}.{} AS
                SELECT *
                FROM {}.{};
                """
            ).format(
                sql.Identifier(serving_schema),
                sql.Identifier("v_demographic_summary"),
                sql.Identifier(analytics_schema),
                sql.Identifier("demographic_summary"),
            ),
        ),
        (
            "v_dashboard_kpis",
            sql.SQL(
                """
                CREATE OR REPLACE VIEW {}.{} AS
                WITH daily AS (
                    SELECT
                        total_patient_events,
                        average_patient_waittime,
                        average_patient_satisfaction_score,
                        null_satisfaction_score_events,
                        (
                            total_patient_events
                            - null_satisfaction_score_events
                        ) AS satisfaction_score_events
                    FROM {}.{}
                )
                SELECT
                    COALESCE(SUM(total_patient_events), 0)::BIGINT
                        AS total_patient_events,
                    (
                        SUM(
                            average_patient_waittime
                            * total_patient_events
                        )
                        / NULLIF(SUM(total_patient_events), 0)
                    ) AS average_waittime_overall,
                    (
                        SUM(
                            average_patient_satisfaction_score
                            * satisfaction_score_events
                        )
                        / NULLIF(SUM(satisfaction_score_events), 0)
                    ) AS average_satisfaction_overall,
                    COUNT(*)::BIGINT AS number_of_daily_points,
                    (
                        SELECT COUNT(*)::BIGINT
                        FROM {}.{}
                    ) AS number_of_department_groups,
                    (
                        SELECT COUNT(*)::BIGINT
                        FROM {}.{}
                    ) AS number_of_demographic_groups
                FROM daily;
                """
            ).format(
                sql.Identifier(serving_schema),
                sql.Identifier("v_dashboard_kpis"),
                sql.Identifier(analytics_schema),
                sql.Identifier("daily_patient_flow"),
                sql.Identifier(analytics_schema),
                sql.Identifier("department_referral_summary"),
                sql.Identifier(analytics_schema),
                sql.Identifier("demographic_summary"),
            ),
        ),
    ]

    with get_postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                    sql.Identifier(serving_schema)
                )
            )
            for _, statement in view_statements:
                cursor.execute(statement)

    return [view_name for view_name, _ in view_statements]


def run_serving_load() -> dict[str, Any]:
    """Load Gold tables and create serving views in PostgreSQL."""
    loaded_tables = load_gold_tables()
    created_views = create_serving_views()
    return {
        "analytics_schema": ANALYTICS_SCHEMA,
        "serving_schema": SERVING_SCHEMA,
        "loaded_tables": loaded_tables,
        "created_views": created_views,
    }
