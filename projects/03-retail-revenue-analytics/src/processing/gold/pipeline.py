from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import path_relative_to_project
from processing.gold.metadata import (
    build_gold_run_metadata,
    describe_output,
    get_gold_output_dir,
    write_gold_run_metadata,
)
from processing.gold.metrics import (
    add_item_revenue_measures,
    aggregate_item_revenue,
    build_kpi_overview,
    summarize_payments,
)
from processing.silver.config import get_silver_tables_dir


REQUIRED_SILVER_TABLES = (
    "orders",
    "order_items",
    "order_payments",
    "products",
    "product_category_name_translation",
    "customers",
    "sellers",
)


def _read_silver_table(table_name: str, silver_tables_dir: Path) -> pd.DataFrame:
    path = silver_tables_dir / f"{table_name}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Required Silver table does not exist: {path}")

    return pd.read_csv(path)


def _build_item_analysis_base(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Build a Gold analysis base at order item grain."""
    order_items = add_item_revenue_measures(tables["order_items"])
    orders = tables["orders"]
    products = tables["products"]
    categories = tables["product_category_name_translation"]
    customers = tables["customers"]
    sellers = tables["sellers"]

    item_data = order_items.merge(
        orders[
            [
                "order_id",
                "customer_id",
                "order_status",
                "order_purchase_timestamp",
            ]
        ],
        on="order_id",
        how="left",
        validate="many_to_one",
    )
    item_data = item_data.merge(
        products[["product_id", "product_category_name"]],
        on="product_id",
        how="left",
        validate="many_to_one",
    )
    item_data = item_data.merge(
        categories[["product_category_name", "product_category_name_english"]],
        on="product_category_name",
        how="left",
        validate="many_to_one",
    )
    item_data = item_data.merge(
        sellers[["seller_id", "seller_state"]],
        on="seller_id",
        how="left",
        validate="many_to_one",
    )
    item_data = item_data.merge(
        customers[["customer_id", "customer_state"]],
        on="customer_id",
        how="left",
        validate="many_to_one",
    )

    item_data["product_category_name"] = item_data["product_category_name"].fillna("unknown")
    item_data["product_category_name_english"] = item_data[
        "product_category_name_english"
    ].fillna(item_data["product_category_name"])
    item_data["order_status"] = item_data["order_status"].fillna("unknown")
    item_data["seller_state"] = item_data["seller_state"].fillna("unknown")
    item_data["customer_state"] = item_data["customer_state"].fillna("unknown")
    item_data["order_purchase_date"] = pd.to_datetime(
        item_data["order_purchase_timestamp"], errors="coerce"
    ).dt.date

    return item_data


def _write_output(dataframe: pd.DataFrame, output_dir: Path, filename: str) -> dict[str, Any]:
    output_path = output_dir / filename
    dataframe.to_csv(output_path, index=False)
    return describe_output(output_path, len(dataframe), len(dataframe.columns))


def run_gold_pipeline(silver_tables_dir: Path | None = None) -> dict[str, Any]:
    """
    Generate Gold v1 revenue and business KPI summaries from Silver tables.

    Sales measures use order_items as the item-side grain. Payment rows are
    summarized separately to avoid duplicating item revenue when an order has
    multiple payment records.
    """
    silver_dir = silver_tables_dir or get_silver_tables_dir()
    tables = {
        table_name: _read_silver_table(table_name, silver_dir)
        for table_name in REQUIRED_SILVER_TABLES
    }

    output_dir = get_gold_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    item_data = _build_item_analysis_base(tables)

    outputs: list[dict[str, Any]] = []

    kpi_overview = build_kpi_overview(
        orders=tables["orders"],
        item_data=item_data,
        payments=tables["order_payments"],
    )
    outputs.append(_write_output(kpi_overview, output_dir, "kpi_overview.csv"))

    daily_revenue_summary = aggregate_item_revenue(
        item_data,
        ["order_purchase_date", "order_status"],
        include_order_count=True,
    ).sort_values(["order_purchase_date", "order_status"])
    outputs.append(
        _write_output(daily_revenue_summary, output_dir, "daily_revenue_summary.csv")
    )

    category_revenue_summary = aggregate_item_revenue(
        item_data,
        ["product_category_name", "product_category_name_english"],
    ).sort_values("gross_merchandise_value", ascending=False)
    outputs.append(
        _write_output(category_revenue_summary, output_dir, "category_revenue_summary.csv")
    )

    seller_revenue_summary = aggregate_item_revenue(
        item_data,
        ["seller_id", "seller_state"],
    ).sort_values("gross_merchandise_value", ascending=False)
    outputs.append(_write_output(seller_revenue_summary, output_dir, "seller_revenue_summary.csv"))

    customer_state_revenue_summary = aggregate_item_revenue(
        item_data,
        ["customer_state"],
        include_order_count=True,
    ).sort_values("gross_merchandise_value", ascending=False)
    outputs.append(
        _write_output(
            customer_state_revenue_summary,
            output_dir,
            "customer_state_revenue_summary.csv",
        )
    )

    payment_type_summary = summarize_payments(tables["order_payments"])
    outputs.append(_write_output(payment_type_summary, output_dir, "payment_type_summary.csv"))

    order_status_summary = aggregate_item_revenue(
        item_data,
        ["order_status"],
        include_order_count=True,
    ).sort_values("gross_merchandise_value", ascending=False)
    outputs.append(_write_output(order_status_summary, output_dir, "order_status_summary.csv"))

    metadata = build_gold_run_metadata(outputs)
    metadata_path = write_gold_run_metadata(metadata)

    return {
        "output_count": len(outputs),
        "outputs": outputs,
        "metadata_path": path_relative_to_project(metadata_path),
    }
