from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb

from config import (
    GOLD_TABLE_NAMES,
    build_gold_metadata_path,
    build_gold_output_file_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
)
from processing.gold.metadata import build_gold_event_date_metadata
from processing.gold.metrics import actor_segment_case_sql, namespace_case_sql
from stream.checkpoints import build_layer_state_template, load_json_document, save_json_document, to_isoformat, utc_now


def discover_silver_event_dates() -> list[str]:
    """Return available Silver event-date partitions."""
    settings = get_settings()
    event_dates = []
    silver_root = settings.silver_tables_dir / "recentchange_events"
    if not silver_root.exists():
        return []

    for partition_path in sorted(silver_root.glob("event_date=*")):
        event_dates.append(partition_path.name.replace("event_date=", "", 1))
    return event_dates


def select_event_dates_to_process(
    available_event_dates: list[str],
    *,
    state: dict[str, Any],
    event_dates: list[str] | None,
    force: bool,
) -> list[str]:
    """Return event dates that should be summarized into Gold."""
    requested = set(event_dates or [])
    selected = []

    for event_date in available_event_dates:
        if requested and event_date not in requested:
            continue
        if force or event_date not in state.get("processed_event_dates", {}):
            selected.append(event_date)
    return selected


def build_minute_event_summary_sql(event_date: str) -> str:
    """Return the SQL used to build minute-level event summaries."""
    return f"""
        SELECT
            CAST('{event_date}' AS DATE) AS event_date,
            event_minute,
            COALESCE(wiki, 'unknown') AS wiki,
            COALESCE(event_type, 'unknown') AS event_type,
            COUNT(*) AS event_count,
            COUNT(DISTINCT NULLIF(user_text, '')) AS unique_user_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'bot' THEN 1 ELSE 0 END) AS bot_event_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'human' THEN 1 ELSE 0 END) AS non_bot_event_count,
            SUM(CASE WHEN event_type = 'edit' THEN 1 ELSE 0 END) AS edit_count,
            SUM(CASE WHEN event_type = 'new' THEN 1 ELSE 0 END) AS new_page_count,
            SUM(CASE WHEN event_type = 'log' THEN 1 ELSE 0 END) AS log_event_count
        FROM silver_events
        GROUP BY 2, 3, 4
        ORDER BY event_minute, wiki, event_type
    """


def build_event_type_summary_sql(event_date: str) -> str:
    """Return the SQL used to build event-type summaries."""
    return f"""
        SELECT
            CAST('{event_date}' AS DATE) AS event_date,
            COALESCE(event_type, 'unknown') AS event_type,
            COUNT(*) AS event_count,
            COUNT(DISTINCT NULLIF(user_text, '')) AS unique_user_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'bot' THEN 1 ELSE 0 END) AS bot_event_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'human' THEN 1 ELSE 0 END) AS non_bot_event_count
        FROM silver_events
        GROUP BY 2
        ORDER BY event_type
    """


def build_bot_vs_human_summary_sql(event_date: str) -> str:
    """Return the SQL used to build actor-segment summaries."""
    return f"""
        SELECT
            CAST('{event_date}' AS DATE) AS event_date,
            {actor_segment_case_sql()} AS actor_segment,
            COUNT(*) AS event_count,
            COUNT(DISTINCT NULLIF(user_text, '')) AS unique_user_count
        FROM silver_events
        GROUP BY 2
        ORDER BY actor_segment
    """


def build_wiki_activity_summary_sql(event_date: str) -> str:
    """Return the SQL used to build wiki activity summaries."""
    return f"""
        SELECT
            CAST('{event_date}' AS DATE) AS event_date,
            COALESCE(wiki, 'unknown') AS wiki,
            COUNT(*) AS event_count,
            COUNT(DISTINCT NULLIF(user_text, '')) AS unique_user_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'bot' THEN 1 ELSE 0 END) AS bot_event_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'human' THEN 1 ELSE 0 END) AS non_bot_event_count,
            SUM(CASE WHEN event_type = 'edit' THEN 1 ELSE 0 END) AS edit_count,
            SUM(CASE WHEN event_type = 'new' THEN 1 ELSE 0 END) AS new_page_count,
            SUM(CASE WHEN event_type = 'log' THEN 1 ELSE 0 END) AS log_event_count
        FROM silver_events
        GROUP BY 2
        ORDER BY event_count DESC, wiki
    """


def build_namespace_activity_summary_sql(event_date: str) -> str:
    """Return the SQL used to build namespace summaries."""
    return f"""
        SELECT
            CAST('{event_date}' AS DATE) AS event_date,
            {namespace_case_sql()} AS namespace,
            COUNT(*) AS event_count,
            COUNT(DISTINCT NULLIF(user_text, '')) AS unique_user_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'bot' THEN 1 ELSE 0 END) AS bot_event_count,
            SUM(CASE WHEN {actor_segment_case_sql()} = 'human' THEN 1 ELSE 0 END) AS non_bot_event_count
        FROM silver_events
        GROUP BY 2
        ORDER BY event_count DESC, namespace
    """


TABLE_SQL_BUILDERS = {
    "minute_event_summary": build_minute_event_summary_sql,
    "event_type_summary": build_event_type_summary_sql,
    "bot_vs_human_summary": build_bot_vs_human_summary_sql,
    "wiki_activity_summary": build_wiki_activity_summary_sql,
    "namespace_activity_summary": build_namespace_activity_summary_sql,
}


def run_gold_pipeline(
    *,
    event_dates: list[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Build Gold summary tables from partitioned Silver event data."""
    settings = get_settings()
    ensure_runtime_directories()
    state = load_json_document(settings.gold_state_path, build_layer_state_template("gold"))

    available_event_dates = discover_silver_event_dates()
    selected_event_dates = select_event_dates_to_process(
        available_event_dates,
        state=state,
        event_dates=event_dates,
        force=force,
    )

    processed_event_dates = []

    for event_date in selected_event_dates:
        started_at = utc_now()
        silver_glob = settings.silver_tables_dir / "recentchange_events" / f"event_date={event_date}" / "*.parquet"
        if not list((settings.silver_tables_dir / "recentchange_events" / f"event_date={event_date}").glob("*.parquet")):
            continue

        connection = duckdb.connect()
        table_output_paths: dict[str, Path] = {}
        table_row_counts: dict[str, int] = {}

        try:
            glob_value = str(silver_glob).replace("'", "''")
            connection.execute(f"CREATE OR REPLACE VIEW silver_events AS SELECT * FROM read_parquet('{glob_value}')")

            for table_name in GOLD_TABLE_NAMES:
                dataframe = connection.execute(TABLE_SQL_BUILDERS[table_name](event_date)).df()
                output_path = build_gold_output_file_path(table_name=table_name, event_date=event_date)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                dataframe.to_parquet(output_path, index=False)
                table_output_paths[table_name] = output_path
                table_row_counts[table_name] = int(len(dataframe.index))
        finally:
            connection.close()

        metadata = build_gold_event_date_metadata(
            event_date=event_date,
            silver_source_glob=path_relative_to_project(silver_glob),
            table_output_paths=table_output_paths,
            table_row_counts=table_row_counts,
            started_at=to_isoformat(started_at),
            finished_at=to_isoformat(utc_now()),
        )
        metadata_path = build_gold_metadata_path(event_date)
        save_json_document(metadata_path, metadata)

        state.setdefault("processed_event_dates", {})
        state["processed_event_dates"][event_date] = {
            "metadata_path": path_relative_to_project(metadata_path),
            "table_row_counts": table_row_counts,
            "table_names": list(table_output_paths.keys()),
        }
        processed_event_dates.append(
            {
                "event_date": event_date,
                "metadata_path": path_relative_to_project(metadata_path),
                "table_row_counts": table_row_counts,
            }
        )

    state["updated_at"] = to_isoformat(utc_now())
    save_json_document(settings.gold_state_path, state)

    summary = {
        "job_name": "gold",
        "available_event_dates": available_event_dates,
        "processed_event_date_count": len(processed_event_dates),
        "processed_event_dates": processed_event_dates,
        "state_path": path_relative_to_project(settings.gold_state_path),
        "force": force,
    }
    save_json_document(settings.latest_gold_run_path, summary)
    return summary
