from __future__ import annotations

from typing import Any

from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError

from config import get_settings


def ensure_topic_exists() -> dict[str, Any]:
    """Ensure the raw event topic exists in the local broker."""
    settings = get_settings()
    admin = KafkaAdminClient(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        client_id=settings.project_name,
    )

    created = False
    try:
        existing_topics = set(admin.list_topics())
        if settings.raw_topic_name not in existing_topics:
            topic = NewTopic(
                name=settings.raw_topic_name,
                num_partitions=settings.kafka_topic_partitions,
                replication_factor=settings.kafka_topic_replication_factor,
            )
            try:
                admin.create_topics([topic], validate_only=False)
                created = True
            except TopicAlreadyExistsError:
                created = False
    finally:
        admin.close()

    return {
        "topic_name": settings.raw_topic_name,
        "bootstrap_servers": settings.kafka_bootstrap_servers,
        "created_now": created,
        "partitions": settings.kafka_topic_partitions,
        "replication_factor": settings.kafka_topic_replication_factor,
    }
