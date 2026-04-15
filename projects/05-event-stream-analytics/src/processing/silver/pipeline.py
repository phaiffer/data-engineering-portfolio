from __future__ import annotations

from pathlib import Path
from typing import Any

from config import (
    build_silver_metadata_path,
    build_silver_output_file_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
)
from processing.silver.metadata import build_silver_batch_metadata
from processing.silver.standardization import standardize_recentchange_records
from quality.checks import run_silver_quality_checks
from stream.checkpoints import build_layer_state_template, load_json_document, save_json_document, to_isoformat, utc_now
from stream.messages import load_jsonl


def discover_bronze_batches() -> list[tuple[str, Path]]:
    """Return the landed Bronze batch files available for standardization."""
    settings = get_settings()
    batches: list[tuple[str, Path]] = []
    for batch_path in sorted(settings.bronze_raw_dir.rglob("batch_*.jsonl")):
        batch_id = batch_path.stem.replace("batch_", "", 1)
        batches.append((batch_id, batch_path))
    return batches


def select_batches_to_process(
    discovered_batches: list[tuple[str, Path]],
    *,
    state: dict[str, Any],
    batch_ids: list[str] | None,
    force: bool,
) -> list[tuple[str, Path]]:
    """Return the Bronze batches that should be standardized."""
    requested = set(batch_ids or [])
    selected: list[tuple[str, Path]] = []

    for batch_id, batch_path in discovered_batches:
        if requested and batch_id not in requested:
            continue
        if force or batch_id not in state.get("processed_batches", {}):
            selected.append((batch_id, batch_path))
    return selected


def run_silver_pipeline(
    *,
    batch_ids: list[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Standardize landed Bronze batches into partitioned Silver Parquet."""
    settings = get_settings()
    ensure_runtime_directories()
    state = load_json_document(settings.silver_state_path, build_layer_state_template("silver"))

    discovered_batches = discover_bronze_batches()
    selected_batches = select_batches_to_process(
        discovered_batches,
        state=state,
        batch_ids=batch_ids,
        force=force,
    )

    processed_batches: list[dict[str, Any]] = []
    written_output_files: list[str] = []

    for batch_id, batch_path in selected_batches:
        started_at = utc_now()
        records = load_jsonl(batch_path)
        dataframe = standardize_recentchange_records(records, source_batch_id=batch_id)
        quality_summary = run_silver_quality_checks(dataframe)

        output_paths = []
        if not dataframe.empty:
            grouped = dataframe.groupby("event_date", dropna=True)
            for event_date, event_date_frame in grouped:
                output_path = build_silver_output_file_path(event_date=str(event_date), batch_id=batch_id)
                output_path.parent.mkdir(parents=True, exist_ok=True)
                event_date_frame.to_parquet(output_path, index=False)
                output_paths.append(output_path)

        metadata = build_silver_batch_metadata(
            batch_id=batch_id,
            source_path=batch_path,
            output_paths=output_paths,
            quality_summary=quality_summary,
            started_at=to_isoformat(started_at),
            finished_at=to_isoformat(utc_now()),
        )
        metadata_path = build_silver_metadata_path(batch_id)
        save_json_document(metadata_path, metadata)

        event_dates_written = metadata["event_dates_written"]
        state["processed_batches"][batch_id] = {
            "source_batch_path": path_relative_to_project(batch_path),
            "metadata_path": path_relative_to_project(metadata_path),
            "event_dates_written": event_dates_written,
            "row_count": quality_summary["row_count"],
        }
        for event_date in event_dates_written:
            state.setdefault("processed_event_dates", {})
            state["processed_event_dates"].setdefault(event_date, {"source_batch_ids": []})
            if batch_id not in state["processed_event_dates"][event_date]["source_batch_ids"]:
                state["processed_event_dates"][event_date]["source_batch_ids"].append(batch_id)

        processed_batches.append(
            {
                "batch_id": batch_id,
                "row_count": quality_summary["row_count"],
                "event_dates_written": event_dates_written,
                "metadata_path": path_relative_to_project(metadata_path),
            }
        )
        written_output_files.extend(metadata["output_files"])

    state["updated_at"] = to_isoformat(utc_now())
    save_json_document(settings.silver_state_path, state)

    summary = {
        "job_name": "silver",
        "discovered_bronze_batches": len(discovered_batches),
        "processed_batch_count": len(processed_batches),
        "processed_batches": processed_batches,
        "written_output_files": written_output_files,
        "state_path": path_relative_to_project(settings.silver_state_path),
        "force": force,
    }
    save_json_document(settings.latest_silver_run_path, summary)
    return summary
