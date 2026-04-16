from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional until project dependencies are installed
    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

GOLD_TABLE_NAMES = (
    "minute_event_summary",
    "event_type_summary",
    "bot_vs_human_summary",
    "wiki_activity_summary",
    "namespace_activity_summary",
)


@dataclass(frozen=True)
class ProjectSettings:
    """Centralize environment-driven settings for the project."""

    project_name: str
    source_stream_url: str
    source_docs_url: str
    source_schema_url: str
    source_stream_name: str
    kafka_bootstrap_servers: str
    raw_topic_name: str
    bronze_consumer_group: str
    default_max_events: int
    default_max_seconds: int
    request_timeout_seconds: int
    http_connect_timeout_seconds: int
    http_read_timeout_seconds: int
    stream_reconnect_seconds: int
    kafka_poll_timeout_ms: int
    kafka_topic_partitions: int
    kafka_topic_replication_factor: int
    bronze_raw_dir: Path
    bronze_metadata_dir: Path
    bronze_state_dir: Path
    bronze_state_path: Path
    publisher_checkpoint_path: Path
    latest_publisher_run_path: Path
    latest_bronze_run_path: Path
    silver_tables_dir: Path
    silver_metadata_dir: Path
    silver_state_dir: Path
    silver_state_path: Path
    latest_silver_run_path: Path
    gold_tables_dir: Path
    gold_metadata_dir: Path
    gold_state_dir: Path
    gold_state_path: Path
    latest_gold_run_path: Path
    operations_metadata_dir: Path
    latest_validation_run_path: Path


def get_project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@lru_cache(maxsize=1)
def get_settings() -> ProjectSettings:
    """Load project settings from environment variables with safe defaults."""
    bronze_raw_dir = PROJECT_ROOT / os.getenv("BRONZE_RAW_DIR", "data/bronze/raw")
    bronze_metadata_dir = PROJECT_ROOT / os.getenv("BRONZE_METADATA_DIR", "data/bronze/metadata")
    bronze_state_dir = PROJECT_ROOT / os.getenv("BRONZE_STATE_DIR", "data/bronze/state")
    silver_tables_dir = PROJECT_ROOT / os.getenv("SILVER_TABLES_DIR", "data/silver/tables")
    silver_metadata_dir = PROJECT_ROOT / os.getenv("SILVER_METADATA_DIR", "data/silver/metadata")
    silver_state_dir = PROJECT_ROOT / os.getenv("SILVER_STATE_DIR", "data/silver/state")
    gold_tables_dir = PROJECT_ROOT / os.getenv("GOLD_TABLES_DIR", "data/gold/tables")
    gold_metadata_dir = PROJECT_ROOT / os.getenv("GOLD_METADATA_DIR", "data/gold/metadata")
    gold_state_dir = PROJECT_ROOT / os.getenv("GOLD_STATE_DIR", "data/gold/state")
    operations_metadata_dir = PROJECT_ROOT / os.getenv("OPERATIONS_METADATA_DIR", "data/operations")

    return ProjectSettings(
        project_name=os.getenv("PROJECT_NAME", "event-stream-analytics"),
        source_stream_url=os.getenv(
            "SOURCE_STREAM_URL",
            "https://stream.wikimedia.org/v2/stream/recentchange",
        ),
        source_docs_url=os.getenv("SOURCE_DOCS_URL", "https://wikitech.wikimedia.org/wiki/EventStreams"),
        source_schema_url=os.getenv(
            "SOURCE_SCHEMA_URL",
            "https://schema.wikimedia.org/repositories/primary/jsonschema/mediawiki/recentchange/latest.yaml",
        ),
        source_stream_name=os.getenv("SOURCE_STREAM_NAME", "recentchange"),
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:19092"),
        raw_topic_name=os.getenv("RAW_TOPIC_NAME", "wikimedia.recentchange.raw"),
        bronze_consumer_group=os.getenv("BRONZE_CONSUMER_GROUP", "event-stream-bronze-consumer"),
        default_max_events=int(os.getenv("DEFAULT_MAX_EVENTS", "100")),
        default_max_seconds=int(os.getenv("DEFAULT_MAX_SECONDS", "60")),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        http_connect_timeout_seconds=int(os.getenv("HTTP_CONNECT_TIMEOUT_SECONDS", "10")),
        http_read_timeout_seconds=int(os.getenv("HTTP_READ_TIMEOUT_SECONDS", "30")),
        stream_reconnect_seconds=int(os.getenv("STREAM_RECONNECT_SECONDS", "2")),
        kafka_poll_timeout_ms=int(os.getenv("KAFKA_POLL_TIMEOUT_MS", "1000")),
        kafka_topic_partitions=int(os.getenv("KAFKA_TOPIC_PARTITIONS", "1")),
        kafka_topic_replication_factor=int(os.getenv("KAFKA_TOPIC_REPLICATION_FACTOR", "1")),
        bronze_raw_dir=bronze_raw_dir,
        bronze_metadata_dir=bronze_metadata_dir,
        bronze_state_dir=bronze_state_dir,
        bronze_state_path=bronze_state_dir / "bronze_state.json",
        publisher_checkpoint_path=bronze_state_dir / "publisher_checkpoint.json",
        latest_publisher_run_path=bronze_metadata_dir / "latest_publisher_run.json",
        latest_bronze_run_path=bronze_metadata_dir / "latest_bronze_run.json",
        silver_tables_dir=silver_tables_dir,
        silver_metadata_dir=silver_metadata_dir,
        silver_state_dir=silver_state_dir,
        silver_state_path=silver_state_dir / "silver_state.json",
        latest_silver_run_path=silver_metadata_dir / "latest_silver_run.json",
        gold_tables_dir=gold_tables_dir,
        gold_metadata_dir=gold_metadata_dir,
        gold_state_dir=gold_state_dir,
        gold_state_path=gold_state_dir / "gold_state.json",
        latest_gold_run_path=gold_metadata_dir / "latest_gold_run.json",
        operations_metadata_dir=operations_metadata_dir,
        latest_validation_run_path=operations_metadata_dir / "latest_validation_run.json",
    )


def ensure_runtime_directories() -> None:
    """Create the runtime directory structure when it does not already exist."""
    settings = get_settings()
    directories: Iterable[Path] = (
        settings.bronze_raw_dir,
        settings.bronze_metadata_dir,
        settings.bronze_state_dir,
        settings.silver_tables_dir,
        settings.silver_metadata_dir,
        settings.silver_state_dir,
        settings.gold_tables_dir,
        settings.gold_metadata_dir,
        settings.gold_state_dir,
        settings.operations_metadata_dir,
    )

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def path_relative_to_project(path: Path) -> str:
    """Return a stable project-relative string path."""
    return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))


def build_bronze_batch_file_path(*, stream_date: str, batch_id: str) -> Path:
    """Return the raw Bronze output path for one landed batch."""
    settings = get_settings()
    return settings.bronze_raw_dir / f"stream_date={stream_date}" / f"batch_{batch_id}.jsonl"


def build_bronze_batch_metadata_path(batch_id: str) -> Path:
    """Return the Bronze metadata path for one landed batch."""
    settings = get_settings()
    return settings.bronze_metadata_dir / f"bronze_batch_{batch_id}.json"


def build_silver_output_file_path(*, event_date: str, batch_id: str) -> Path:
    """Return the partitioned Silver output path for one standardized batch slice."""
    settings = get_settings()
    return (
        settings.silver_tables_dir
        / "recentchange_events"
        / f"event_date={event_date}"
        / f"batch_{batch_id}.parquet"
    )


def build_silver_metadata_path(batch_id: str) -> Path:
    """Return the Silver metadata path for one processed Bronze batch."""
    settings = get_settings()
    return settings.silver_metadata_dir / f"silver_batch_{batch_id}.json"


def build_gold_output_file_path(*, table_name: str, event_date: str) -> Path:
    """Return the Gold output path for one event-date summary table."""
    settings = get_settings()
    return settings.gold_tables_dir / table_name / f"event_date={event_date}" / f"{table_name}.parquet"


def build_gold_metadata_path(event_date: str) -> Path:
    """Return the Gold metadata path for one summarized event date."""
    settings = get_settings()
    return settings.gold_metadata_dir / f"gold_event_date_{event_date}.json"
