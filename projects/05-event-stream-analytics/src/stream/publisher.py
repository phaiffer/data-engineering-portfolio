from __future__ import annotations

import json
from typing import Any

from kafka import KafkaProducer

from broker.topics import ensure_topic_exists
from config import get_settings, ensure_runtime_directories, path_relative_to_project
from stream.checkpoints import (
    build_publisher_checkpoint_template,
    load_json_document,
    save_json_document,
    should_stop_bounded_run,
    to_isoformat,
    update_publisher_checkpoint,
    utc_now,
)
from stream.messages import build_broker_message, is_canary_event, make_run_id
from stream.source_client import WikimediaSourceClient


def create_kafka_producer() -> KafkaProducer:
    """Create the Kafka-compatible producer used by the publisher."""
    settings = get_settings()
    return KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda value: value.encode("utf-8"),
    )


def build_publisher_run_metadata(
    *,
    run_id: str,
    started_at: str,
    finished_at: str,
    max_events: int | None,
    max_seconds: int | None,
    published_count: int,
    filtered_canary_count: int,
    resumed_from_checkpoint: bool,
    topic_summary: dict[str, Any],
    last_source_meta_id: str | None,
    last_sse_event_id: str | None,
    stop_reason: str | None,
) -> dict[str, Any]:
    """Build a stable publisher run summary."""
    return {
        "run_id": run_id,
        "job_name": "publisher",
        "started_at": started_at,
        "finished_at": finished_at,
        "max_events": max_events,
        "max_seconds": max_seconds,
        "published_count": published_count,
        "filtered_canary_count": filtered_canary_count,
        "resumed_from_checkpoint": resumed_from_checkpoint,
        "topic": topic_summary,
        "last_source_meta_id": last_source_meta_id,
        "last_sse_event_id": last_sse_event_id,
        "stop_reason": stop_reason,
    }


def run_publisher(
    *,
    max_events: int | None = None,
    max_seconds: int | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Read the live stream and publish a bounded sample into Redpanda."""
    settings = get_settings()
    ensure_runtime_directories()
    topic_summary = ensure_topic_exists()

    effective_max_events = max_events or settings.default_max_events
    effective_max_seconds = max_seconds or settings.default_max_seconds

    checkpoint = load_json_document(
        settings.publisher_checkpoint_path,
        build_publisher_checkpoint_template(),
    )
    resume_event_id = None if force else checkpoint.get("last_sse_event_id")
    resumed_from_checkpoint = bool(resume_event_id)

    run_started_at = utc_now()
    run_id = make_run_id(run_started_at)
    producer = create_kafka_producer()
    source_client = WikimediaSourceClient()

    published_count = 0
    filtered_canary_count = 0
    last_source_meta_id: str | None = None
    last_sse_event_id: str | None = resume_event_id
    stop_reason: str | None = None

    try:
        for source_event in source_client.stream_recent_changes(
            max_seconds=effective_max_seconds,
            last_event_id=resume_event_id,
        ):
            if is_canary_event(source_event.payload):
                filtered_canary_count += 1
                continue

            published_at = utc_now()
            message = build_broker_message(
                source_event.payload,
                sse_event_id=source_event.event_id,
                publisher_run_id=run_id,
                source_url=settings.source_stream_url,
                published_at=published_at,
            )
            message_key = message["publisher"]["message_key"]
            producer.send(settings.raw_topic_name, key=message_key, value=message).get(timeout=10)

            published_count += 1
            last_source_meta_id = source_event.payload.get("meta", {}).get("id")
            last_sse_event_id = source_event.event_id or last_sse_event_id

            update_publisher_checkpoint(
                checkpoint,
                run_id=run_id,
                sse_event_id=last_sse_event_id,
                source_meta_id=last_source_meta_id,
                event_timestamp=source_event.payload.get("meta", {}).get("dt"),
            )

            stop_reason = should_stop_bounded_run(
                started_at=run_started_at,
                now=utc_now(),
                processed_count=published_count,
                max_events=effective_max_events,
                max_seconds=effective_max_seconds,
            )
            if stop_reason:
                break
    finally:
        producer.flush()
        producer.close()

    save_json_document(settings.publisher_checkpoint_path, checkpoint)

    run_finished_at = utc_now()
    metadata = build_publisher_run_metadata(
        run_id=run_id,
        started_at=to_isoformat(run_started_at),
        finished_at=to_isoformat(run_finished_at),
        max_events=effective_max_events,
        max_seconds=effective_max_seconds,
        published_count=published_count,
        filtered_canary_count=filtered_canary_count,
        resumed_from_checkpoint=resumed_from_checkpoint,
        topic_summary=topic_summary,
        last_source_meta_id=last_source_meta_id,
        last_sse_event_id=last_sse_event_id,
        stop_reason=stop_reason,
    )

    run_metadata_path = settings.bronze_metadata_dir / f"publisher_run_{run_id}.json"
    save_json_document(run_metadata_path, metadata)
    save_json_document(settings.latest_publisher_run_path, metadata)

    metadata["publisher_checkpoint_path"] = path_relative_to_project(settings.publisher_checkpoint_path)
    metadata["metadata_path"] = path_relative_to_project(run_metadata_path)
    return metadata
