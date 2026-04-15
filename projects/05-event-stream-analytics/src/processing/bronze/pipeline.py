from __future__ import annotations

from typing import Any

from broker.topics import ensure_topic_exists
from config import (
    build_bronze_batch_file_path,
    build_bronze_batch_metadata_path,
    ensure_runtime_directories,
    get_settings,
    path_relative_to_project,
)
from ingestion.bronze_consumer import consume_broker_messages
from processing.bronze.metadata import build_bronze_batch_metadata
from stream.checkpoints import (
    build_consumer_checkpoint_template,
    load_json_document,
    save_json_document,
    to_isoformat,
)
from stream.messages import make_run_id, write_jsonl


def run_bronze_pipeline(
    *,
    max_events: int | None = None,
    max_seconds: int | None = None,
    replay: bool = False,
) -> dict[str, Any]:
    """Consume broker messages and land a raw Bronze batch locally."""
    settings = get_settings()
    ensure_runtime_directories()
    topic_summary = ensure_topic_exists()

    result = consume_broker_messages(
        max_events=max_events,
        max_seconds=max_seconds,
        replay=replay,
    )

    if not result["records"]:
        summary = {
            "job_name": "bronze_consumer",
            "landed_event_count": 0,
            "resume_strategy": result["resume_strategy"],
            "stop_reason": result["stop_reason"],
            "topic": topic_summary,
            "started_at": to_isoformat(result["started_at"]),
            "finished_at": to_isoformat(result["finished_at"]),
            "max_events": result["max_events"],
            "max_seconds": result["max_seconds"],
        }
        save_json_document(settings.latest_bronze_run_path, summary)
        return summary

    batch_id = make_run_id(result["started_at"])
    stream_date = result["started_at"].strftime("%Y-%m-%d")
    batch_path = build_bronze_batch_file_path(stream_date=stream_date, batch_id=batch_id)
    write_jsonl(batch_path, result["records"])

    metadata = build_bronze_batch_metadata(
        batch_id=batch_id,
        batch_path=batch_path,
        records=result["records"],
        started_at=to_isoformat(result["started_at"]),
        finished_at=to_isoformat(result["finished_at"]),
        max_events=result["max_events"],
        max_seconds=result["max_seconds"],
        resume_strategy=result["resume_strategy"],
        stop_reason=result["stop_reason"],
        observed_partitions=result["observed_partitions"],
    )

    metadata_path = build_bronze_batch_metadata_path(batch_id)
    save_json_document(metadata_path, metadata)

    state = load_json_document(
        settings.bronze_state_path,
        build_consumer_checkpoint_template(
            topic=settings.raw_topic_name,
            consumer_group=settings.bronze_consumer_group,
        ),
    )
    state["partition_offsets"] = result["checkpoint"].get("partition_offsets", {})
    state["processed_batches"][batch_id] = {
        "batch_path": path_relative_to_project(batch_path),
        "metadata_path": path_relative_to_project(metadata_path),
        "landed_event_count": len(result["records"]),
        "stream_date": stream_date,
    }
    state["updated_at"] = to_isoformat(result["finished_at"])
    save_json_document(settings.bronze_state_path, state)

    summary = {
        **metadata,
        "topic": topic_summary,
        "metadata_path": path_relative_to_project(metadata_path),
        "state_path": path_relative_to_project(settings.bronze_state_path),
    }
    save_json_document(settings.latest_bronze_run_path, summary)
    return summary
