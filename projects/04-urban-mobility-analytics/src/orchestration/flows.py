from __future__ import annotations

from typing import Any

from config import resolve_month_window
from ingestion.sources import build_download_plan, run_ingestion_pipeline
from processing.bronze.pipeline import run_bronze_pipeline
from processing.gold.pipeline import run_gold_pipeline
from processing.silver.pipeline import run_silver_pipeline

try:
    from prefect import flow, get_run_logger, task
except ImportError as exc:  # pragma: no cover - exercised only when Prefect is unavailable
    raise ImportError(
        "Prefect is required for orchestration. Install project dependencies first."
    ) from exc


@task(name="plan-source-months")
def plan_source_months(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Resolve the month window and produce a readable source plan."""
    months = resolve_month_window(start_month=start_month, end_month=end_month)
    plan = build_download_plan(months, force=force)
    return {
        "months": [month.month_id for month in months],
        "plan": plan,
        "force": force,
    }


@task(name="run-ingestion")
def run_ingestion_task(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run official-source monthly landing."""
    return run_ingestion_pipeline(start_month=start_month, end_month=end_month, force=force)


@task(name="run-bronze-metadata")
def run_bronze_task(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run Bronze metadata generation over landed months."""
    return run_bronze_pipeline(start_month=start_month, end_month=end_month, force=force)


@task(name="run-silver-standardization")
def run_silver_task(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run Silver standardization for the selected month window."""
    return run_silver_pipeline(start_month=start_month, end_month=end_month, force=force)


@task(name="run-gold-summaries")
def run_gold_task(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run Gold operational summaries for the selected month window."""
    return run_gold_pipeline(start_month=start_month, end_month=end_month, force=force)


@flow(name="urban-mobility-analytics-flow")
def run_urban_mobility_flow(
    start_month: str | None = None,
    end_month: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Run the local-first end-to-end orchestration flow for project 04."""
    logger = get_run_logger()

    source_plan = plan_source_months(
        start_month=start_month,
        end_month=end_month,
        force=force,
    )
    logger.info("Planned source months: %s", ", ".join(source_plan["months"]))

    ingestion_summary = run_ingestion_task(
        start_month=start_month,
        end_month=end_month,
        force=force,
    )
    bronze_summary = run_bronze_task(
        start_month=start_month,
        end_month=end_month,
        force=force,
    )
    silver_summary = run_silver_task(
        start_month=start_month,
        end_month=end_month,
        force=force,
    )
    gold_summary = run_gold_task(
        start_month=start_month,
        end_month=end_month,
        force=force,
    )

    return {
        "plan": source_plan,
        "ingestion": ingestion_summary,
        "bronze": bronze_summary,
        "silver": silver_summary,
        "gold": gold_summary,
    }
