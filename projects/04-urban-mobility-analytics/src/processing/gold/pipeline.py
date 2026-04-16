from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import duckdb
import pandas as pd

from config import (
    MonthPartition,
    build_gold_output_file_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
    resolve_month_window,
)
from ingestion.state import (
    get_current_timestamp,
    get_month_entry,
    mark_month_completed,
    read_state,
    select_months_to_process,
    write_state,
)
from processing.gold.metadata import (
    build_gold_month_metadata,
    build_gold_run_metadata,
    describe_table_output,
    write_gold_month_metadata,
    write_gold_run_metadata,
)
from processing.gold.metrics import (
    build_fare_amount_bucket_case_sql,
    build_payment_type_case_sql,
    build_trip_distance_bucket_case_sql,
)


GOLD_TABLE_QUERIES = {
    "daily_trip_summary": """
        SELECT
            COALESCE(pickup_year, source_year) AS pickup_year,
            COALESCE(pickup_month, source_month) AS pickup_month,
            CAST(pickup_date AS DATE) AS pickup_date,
            COUNT(*) AS trip_count,
            CAST(SUM(COALESCE(passenger_count, 0)) AS BIGINT) AS passenger_count_sum,
            ROUND(SUM(COALESCE(fare_amount, 0)), 2) AS total_fare_amount,
            ROUND(SUM(COALESCE(tip_amount, 0)), 2) AS total_tip_amount,
            ROUND(SUM(COALESCE(tolls_amount, 0)), 2) AS total_tolls_amount,
            ROUND(AVG(trip_distance), 2) AS average_trip_distance,
            ROUND(AVG(total_amount), 2) AS average_total_amount,
            ROUND(AVG(fare_amount), 2) AS average_fare_amount
        FROM silver_trips
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, 3
    """,
    "hourly_trip_summary": """
        SELECT
            COALESCE(pickup_year, source_year) AS pickup_year,
            COALESCE(pickup_month, source_month) AS pickup_month,
            CAST(pickup_date AS DATE) AS pickup_date,
            COALESCE(pickup_hour, -1) AS pickup_hour,
            COUNT(*) AS trip_count,
            CAST(SUM(COALESCE(passenger_count, 0)) AS BIGINT) AS passenger_count_sum,
            ROUND(SUM(COALESCE(fare_amount, 0)), 2) AS total_fare_amount,
            ROUND(SUM(COALESCE(tip_amount, 0)), 2) AS total_tip_amount,
            ROUND(SUM(COALESCE(tolls_amount, 0)), 2) AS total_tolls_amount,
            ROUND(AVG(trip_distance), 2) AS average_trip_distance,
            ROUND(AVG(total_amount), 2) AS average_total_amount,
            ROUND(AVG(fare_amount), 2) AS average_fare_amount
        FROM silver_trips
        GROUP BY 1, 2, 3, 4
        ORDER BY 1, 2, 3, 4
    """,
    "payment_type_summary": f"""
        SELECT
            COALESCE(pickup_year, source_year) AS pickup_year,
            COALESCE(pickup_month, source_month) AS pickup_month,
            payment_type AS payment_type_code,
            {build_payment_type_case_sql("payment_type")} AS payment_type_label,
            COUNT(*) AS trip_count,
            ROUND(SUM(COALESCE(fare_amount, 0)), 2) AS total_fare_amount,
            ROUND(SUM(COALESCE(tip_amount, 0)), 2) AS total_tip_amount,
            ROUND(SUM(COALESCE(total_amount, 0)), 2) AS total_amount,
            ROUND(AVG(total_amount), 2) AS average_total_amount
        FROM silver_trips
        GROUP BY 1, 2, 3, 4
        ORDER BY 1, 2, total_amount DESC, payment_type_code
    """,
    "trip_distance_summary": f"""
        SELECT
            COALESCE(pickup_year, source_year) AS pickup_year,
            COALESCE(pickup_month, source_month) AS pickup_month,
            {build_trip_distance_bucket_case_sql("trip_distance")} AS trip_distance_bucket,
            COUNT(*) AS trip_count,
            ROUND(AVG(trip_distance), 2) AS average_trip_distance,
            ROUND(SUM(COALESCE(total_amount, 0)), 2) AS total_amount
        FROM silver_trips
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, trip_count DESC, trip_distance_bucket
    """,
    "fare_amount_summary": f"""
        SELECT
            COALESCE(pickup_year, source_year) AS pickup_year,
            COALESCE(pickup_month, source_month) AS pickup_month,
            {build_fare_amount_bucket_case_sql("fare_amount")} AS fare_amount_bucket,
            COUNT(*) AS trip_count,
            ROUND(SUM(COALESCE(fare_amount, 0)), 2) AS total_fare_amount,
            ROUND(AVG(fare_amount), 2) AS average_fare_amount,
            ROUND(AVG(total_amount), 2) AS average_total_amount
        FROM silver_trips
        GROUP BY 1, 2, 3
        ORDER BY 1, 2, trip_count DESC, fare_amount_bucket
    """,
}


def _get_silver_files_for_month(source_month: MonthPartition) -> list[Path]:
    settings = get_settings()
    pattern = f"{settings.dataset_slug}_trips_{source_month.month_id}.parquet"
    return sorted((settings.silver_tables_dir / "trips").glob(f"**/{pattern}"))


def _clear_existing_month_outputs(table_name: str, source_month: MonthPartition) -> None:
    pattern = f"{table_name}_{source_month.month_id}.parquet"
    table_root = get_settings().gold_tables_dir / table_name
    if not table_root.exists():
        return

    for path in table_root.glob(f"**/{pattern}"):
        path.unlink()


def _write_partitioned_gold_output(
    dataframe: pd.DataFrame,
    *,
    table_name: str,
    source_month: MonthPartition,
) -> list[dict[str, Any]]:
    table_results: list[dict[str, Any]] = []
    grouped = dataframe.groupby(["pickup_year", "pickup_month"], dropna=False, sort=True)

    for (partition_year, partition_month), partition_frame in grouped:
        output_path = build_gold_output_file_path(
            table_name=table_name,
            source_month=source_month,
            partition_year=int(partition_year),
            partition_month=int(partition_month),
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        partition_frame.to_parquet(output_path, index=False)
        table_results.append(
            describe_table_output(
                output_path,
                row_count=len(partition_frame),
                column_count=len(partition_frame.columns),
            )
        )

    return table_results


def _run_month_queries(source_month: MonthPartition, silver_files: list[Path]) -> list[dict[str, Any]]:
    connection = duckdb.connect(database=":memory:")
    try:
        connection.read_parquet([str(path) for path in silver_files]).create_view("silver_trips")
        table_results: list[dict[str, Any]] = []

        for table_name, query in GOLD_TABLE_QUERIES.items():
            dataframe = connection.execute(query).fetchdf()
            _clear_existing_month_outputs(table_name, source_month)
            outputs = _write_partitioned_gold_output(
                dataframe,
                table_name=table_name,
                source_month=source_month,
            )
            table_results.append(
                {
                    "table_name": table_name,
                    "output_count": len(outputs),
                    "outputs": outputs,
                }
            )

        return table_results
    finally:
        connection.close()


def run_gold_pipeline(
    *,
    months: Sequence[MonthPartition] | None = None,
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Build monthly Gold operational summaries from the partitioned Silver dataset."""
    ensure_runtime_directories()
    run_started_at_utc = get_current_timestamp()
    settings = get_settings()
    selected_months = list(months or resolve_month_window(start_month=start_month, end_month=end_month))
    gold_state = read_state(settings.gold_state_path, "gold")
    months_to_process = select_months_to_process(selected_months, gold_state, force=force)
    months_to_process_keys = {month.month_id for month in months_to_process}

    results: list[dict[str, Any]] = []

    for month in selected_months:
        if month.month_id not in months_to_process_keys:
            existing_entry = get_month_entry(gold_state, month) or {}
            results.append(
                {
                    "source_month": month.month_id,
                    "status": "skipped",
                    "reason": "already_processed",
                    "metadata_path": existing_entry.get("metadata_path"),
                }
            )
            continue

        silver_files = _get_silver_files_for_month(month)
        if not silver_files:
            raise FileNotFoundError(
                "No Silver files were found for month "
                f"{month.month_id}. Run the Silver pipeline first."
            )

        table_results = _run_month_queries(month, silver_files)
        metadata = build_gold_month_metadata(
            month_partition=month,
            table_results=table_results,
        )
        metadata_path = write_gold_month_metadata(metadata)
        output_paths = [
            output["output_path"]
            for table_result in table_results
            for output in table_result["outputs"]
        ]

        gold_state = mark_month_completed(
            gold_state,
            month,
            {
                "metadata_path": path_relative_to_project(metadata_path),
                "table_count": metadata["table_count"],
                "table_names": [table_result["table_name"] for table_result in table_results],
            },
        )
        results.append(
            {
                "source_month": month.month_id,
                "status": "processed",
                "metadata_path": path_relative_to_project(metadata_path),
                "output_files": output_paths,
                "table_count": metadata["table_count"],
            }
        )

    state_path = write_state(settings.gold_state_path, gold_state)
    run_metadata = build_gold_run_metadata(
        selected_months=[month.month_id for month in selected_months],
        results=results,
        force=force,
        run_started_at_utc=run_started_at_utc,
    )
    run_metadata["state_path"] = path_relative_to_project(state_path)
    run_metadata_path = write_gold_run_metadata(run_metadata)

    return {
        **run_metadata,
        "run_metadata_path": path_relative_to_project(run_metadata_path),
    }
