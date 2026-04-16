from __future__ import annotations

from pathlib import Path
from typing import Any

from config import GOLD_TABLE_NAMES, get_settings, path_relative_to_project
from stream.checkpoints import load_json_document, save_json_document, to_isoformat, utc_now


def count_jsonl_rows(path: Path) -> int:
    """Return the number of non-empty JSONL rows in a local file."""
    if not path.exists():
        return 0

    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def safe_load_json(path: Path) -> dict[str, Any]:
    """Load a JSON artifact when it exists, otherwise return an empty document."""
    return load_json_document(path, {})


def summarize_bronze_files() -> dict[str, Any]:
    """Summarize landed Bronze batch files for reviewer validation."""
    settings = get_settings()
    batch_files = sorted(settings.bronze_raw_dir.rglob("batch_*.jsonl"))
    return {
        "batch_file_count": len(batch_files),
        "total_jsonl_rows": sum(count_jsonl_rows(path) for path in batch_files),
        "latest_batch_files": [path_relative_to_project(path) for path in batch_files[-5:]],
    }


def summarize_silver_files() -> dict[str, Any]:
    """Summarize partitioned Silver Parquet files for reviewer validation."""
    settings = get_settings()
    silver_root = settings.silver_tables_dir / "recentchange_events"
    parquet_files = sorted(silver_root.rglob("*.parquet")) if silver_root.exists() else []
    event_dates = sorted(
        {
            path.parent.name.replace("event_date=", "", 1)
            for path in parquet_files
            if path.parent.name.startswith("event_date=")
        }
    )
    return {
        "parquet_file_count": len(parquet_files),
        "event_dates": event_dates,
        "latest_parquet_files": [path_relative_to_project(path) for path in parquet_files[-5:]],
    }


def summarize_gold_files() -> dict[str, Any]:
    """Summarize local Gold summary outputs for reviewer validation."""
    settings = get_settings()
    table_summaries: dict[str, Any] = {}
    for table_name in GOLD_TABLE_NAMES:
        table_root = settings.gold_tables_dir / table_name
        parquet_files = sorted(table_root.rglob("*.parquet")) if table_root.exists() else []
        event_dates = sorted(
            {
                path.parent.name.replace("event_date=", "", 1)
                for path in parquet_files
                if path.parent.name.startswith("event_date=")
            }
        )
        table_summaries[table_name] = {
            "parquet_file_count": len(parquet_files),
            "event_dates": event_dates,
        }

    return {"tables": table_summaries}


def infer_validation_status(manifest: dict[str, Any]) -> str:
    """Return a compact status label for the local validation surface."""
    if manifest["bronze_files"]["batch_file_count"] == 0:
        return "no_bronze_batches"
    if manifest["silver_files"]["parquet_file_count"] == 0:
        return "bronze_only"

    gold_tables = manifest["gold_files"]["tables"].values()
    if not any(table["parquet_file_count"] for table in gold_tables):
        return "silver_ready"

    return "gold_ready"


def build_validation_manifest(*, mode: str) -> dict[str, Any]:
    """Build a single local manifest from checkpoints, metadata, and output files."""
    settings = get_settings()
    publisher_run = safe_load_json(settings.latest_publisher_run_path)
    bronze_run = safe_load_json(settings.latest_bronze_run_path)
    silver_run = safe_load_json(settings.latest_silver_run_path)
    gold_run = safe_load_json(settings.latest_gold_run_path)

    manifest = {
        "job_name": "validation",
        "validated_at": to_isoformat(utc_now()),
        "mode": mode,
        "status": "unknown",
        "latest_runs": {
            "publisher": {
                "path": path_relative_to_project(settings.latest_publisher_run_path),
                "exists": settings.latest_publisher_run_path.exists(),
                "events_published": publisher_run.get("published_count", 0),
                "status": publisher_run.get("stop_reason"),
            },
            "bronze": {
                "path": path_relative_to_project(settings.latest_bronze_run_path),
                "exists": settings.latest_bronze_run_path.exists(),
                "events_consumed": bronze_run.get("landed_event_count", 0),
                "mode": bronze_run.get("resume_strategy"),
                "status": bronze_run.get("stop_reason"),
            },
            "silver": {
                "path": path_relative_to_project(settings.latest_silver_run_path),
                "exists": settings.latest_silver_run_path.exists(),
                "batches_processed": silver_run.get("processed_batch_count", 0),
                "force": silver_run.get("force"),
            },
            "gold": {
                "path": path_relative_to_project(settings.latest_gold_run_path),
                "exists": settings.latest_gold_run_path.exists(),
                "dates_processed": gold_run.get("processed_event_date_count", 0),
                "force": gold_run.get("force"),
            },
        },
        "checkpoints": {
            "publisher": {
                "path": path_relative_to_project(settings.publisher_checkpoint_path),
                "exists": settings.publisher_checkpoint_path.exists(),
            },
            "bronze_consumer": {
                "path": path_relative_to_project(settings.bronze_state_path),
                "exists": settings.bronze_state_path.exists(),
            },
            "silver": {
                "path": path_relative_to_project(settings.silver_state_path),
                "exists": settings.silver_state_path.exists(),
            },
            "gold": {
                "path": path_relative_to_project(settings.gold_state_path),
                "exists": settings.gold_state_path.exists(),
            },
        },
        "bronze_files": summarize_bronze_files(),
        "silver_files": summarize_silver_files(),
        "gold_files": summarize_gold_files(),
    }
    manifest["status"] = infer_validation_status(manifest)
    return manifest


def write_validation_manifest(*, mode: str = "normal") -> dict[str, Any]:
    """Persist the latest validation manifest and return it for CLI output."""
    settings = get_settings()
    manifest = build_validation_manifest(mode=mode)
    save_json_document(settings.latest_validation_run_path, manifest)
    manifest["metadata_path"] = path_relative_to_project(settings.latest_validation_run_path)
    return manifest
