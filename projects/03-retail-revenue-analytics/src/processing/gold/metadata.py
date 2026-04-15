from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ingestion.raw_inventory import DATASET_HANDLE, get_project_root, path_relative_to_project


GOLD_REVENUE_DEFINITIONS = [
    "item_revenue = sum(order_items.price).",
    "freight_value = sum(order_items.freight_value).",
    "gross_merchandise_value = sum(order_items.price + order_items.freight_value).",
    "Payment values are summarized separately and are not joined to item rows for sales totals.",
]

GOLD_LIMITATIONS = [
    "Gold v1 is not a finished accounting model and does not reconcile refunds, cancellations, chargebacks, or settlement timing.",
    "Gold v1 is not a final dimensional mart design.",
    "Order status is retained in status-sensitive outputs so users can decide whether to filter to delivered orders later.",
    "Payments can have multiple rows per order, so they are not naively joined to order_items for revenue calculations.",
]


def get_gold_output_dir() -> Path:
    """Return the directory for Gold analytical CSV artifacts."""
    return get_project_root() / "data" / "gold" / "outputs"


def get_gold_metadata_dir() -> Path:
    """Return the directory for Gold metadata artifacts."""
    return get_project_root() / "data" / "gold" / "metadata"


def build_gold_run_metadata(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    """Build run-level metadata for Gold v1 outputs."""
    return {
        "dataset_handle": DATASET_HANDLE,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "layer": "gold",
        "outputs": outputs,
        "data_sources_used": [
            "silver.orders",
            "silver.order_items",
            "silver.order_payments",
            "silver.products",
            "silver.product_category_name_translation",
            "silver.customers",
            "silver.sellers",
        ],
        "revenue_definitions": GOLD_REVENUE_DEFINITIONS,
        "limitations": GOLD_LIMITATIONS,
    }


def write_gold_run_metadata(metadata: dict[str, Any], output_dir: Path | None = None) -> Path:
    """Write run-level Gold metadata."""
    target_dir = output_dir or get_gold_metadata_dir()
    target_dir.mkdir(parents=True, exist_ok=True)

    output_path = target_dir / "gold_run_summary.json"
    output_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_path


def describe_output(path: Path, row_count: int, column_count: int) -> dict[str, Any]:
    """Return serializable metadata for one Gold output file."""
    return {
        "output_file": path_relative_to_project(path),
        "row_count": int(row_count),
        "column_count": int(column_count),
    }
