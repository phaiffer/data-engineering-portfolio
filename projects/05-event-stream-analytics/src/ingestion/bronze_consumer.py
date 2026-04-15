from __future__ import annotations

import json
from typing import Any

from kafka import KafkaConsumer, TopicPartition

from config import get_settings
from stream.checkpoints import (
    build_consumer_checkpoint_template,
    get_resume_offsets,
    load_json_document,
    should_stop_bounded_run,
    to_isoformat,
    update_partition_checkpoint,
    utc_now,
)


def create_consumer() -> KafkaConsumer:
    """Create the Kafka-compatible Bronze consumer."""
    settings = get_settings()
    return KafkaConsumer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        enable_auto_commit=False,
        auto_offset_reset="earliest",
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
        key_deserializer=lambda value: value.decode("utf-8") if value is not None else None,
    )


def assign_consumer_offsets(
    consumer: KafkaConsumer,
    *,
    replay: bool,
) -> tuple[dict[str, Any], str]:
    """Assign the topic partitions and seek to the correct local resume offsets."""
    settings = get_settings()
    checkpoint = load_json_document(
        settings.bronze_state_path,
        build_consumer_checkpoint_template(
            topic=settings.raw_topic_name,
            consumer_group=settings.bronze_consumer_group,
        ),
    )

    partitions = consumer.partitions_for_topic(settings.raw_topic_name)
    if not partitions:
        raise RuntimeError(
            f"Topic {settings.raw_topic_name!r} was not found in broker {settings.kafka_bootstrap_servers!r}."
        )

    topic_partitions = [TopicPartition(settings.raw_topic_name, partition) for partition in sorted(partitions)]
    consumer.assign(topic_partitions)

    if replay:
        consumer.seek_to_beginning(*topic_partitions)
        return checkpoint, "broker_replay_earliest"

    resume_offsets = get_resume_offsets(checkpoint)
    if not resume_offsets:
        consumer.seek_to_beginning(*topic_partitions)
        return checkpoint, "earliest_without_checkpoint"

    missing_offsets: list[TopicPartition] = []
    for topic_partition in topic_partitions:
        next_offset = resume_offsets.get((topic_partition.topic, topic_partition.partition))
        if next_offset is None:
            missing_offsets.append(topic_partition)
            continue
        consumer.seek(topic_partition, next_offset)

    if missing_offsets:
        consumer.seek_to_beginning(*missing_offsets)

    return checkpoint, "checkpoint_resume"


def consume_broker_messages(
    *,
    max_events: int | None,
    max_seconds: int | None,
    replay: bool,
) -> dict[str, Any]:
    """Consume a bounded set of broker messages and return the landed records."""
    settings = get_settings()
    effective_max_events = max_events or settings.default_max_events
    effective_max_seconds = max_seconds or settings.default_max_seconds

    consumer = create_consumer()
    checkpoint, resume_strategy = assign_consumer_offsets(consumer, replay=replay)

    started_at = utc_now()
    records: list[dict[str, Any]] = []
    observed_partitions: dict[str, dict[str, Any]] = {}
    stop_reason: str | None = None

    try:
        while True:
            polled = consumer.poll(timeout_ms=settings.kafka_poll_timeout_ms)

            for messages in polled.values():
                for message in messages:
                    record = {
                        "broker": {
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "timestamp_ms": message.timestamp,
                            "message_key": message.key,
                        },
                        "consumer": {
                            "consumer_group": settings.bronze_consumer_group,
                            "consumed_at": to_isoformat(utc_now()),
                        },
                        **message.value,
                    }
                    records.append(record)

                    update_partition_checkpoint(
                        checkpoint,
                        topic=message.topic,
                        partition=message.partition,
                        offset=message.offset,
                        broker_timestamp_ms=message.timestamp,
                    )
                    observed_partitions[f"{message.topic}:{message.partition}"] = {
                        "topic": message.topic,
                        "partition": message.partition,
                        "last_offset": message.offset,
                        "last_timestamp_ms": message.timestamp,
                    }

                    stop_reason = should_stop_bounded_run(
                        started_at=started_at,
                        now=utc_now(),
                        processed_count=len(records),
                        max_events=effective_max_events,
                        max_seconds=effective_max_seconds,
                    )
                    if stop_reason:
                        break

                if stop_reason:
                    break

            if stop_reason:
                break

            stop_reason = should_stop_bounded_run(
                started_at=started_at,
                now=utc_now(),
                processed_count=len(records),
                max_events=effective_max_events,
                max_seconds=effective_max_seconds,
            )
            if stop_reason:
                break
    finally:
        consumer.close()

    return {
        "records": records,
        "checkpoint": checkpoint,
        "resume_strategy": resume_strategy,
        "started_at": started_at,
        "finished_at": utc_now(),
        "stop_reason": stop_reason,
        "max_events": effective_max_events,
        "max_seconds": effective_max_seconds,
        "observed_partitions": observed_partitions,
    }
