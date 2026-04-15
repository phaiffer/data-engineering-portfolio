from __future__ import annotations

import pandas as pd


REVENUE_COLUMNS = ["price", "freight_value"]


def add_item_revenue_measures(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add item-side revenue measures without using payment rows as sales grain."""
    enriched = dataframe.copy()

    for column in REVENUE_COLUMNS:
        if column not in enriched.columns:
            enriched[column] = 0
        enriched[column] = pd.to_numeric(enriched[column], errors="coerce").fillna(0)

    enriched["item_revenue"] = enriched["price"]
    enriched["gross_merchandise_value"] = enriched["price"] + enriched["freight_value"]
    return enriched


def aggregate_item_revenue(
    dataframe: pd.DataFrame,
    group_columns: list[str],
    *,
    include_order_count: bool = False,
) -> pd.DataFrame:
    """Aggregate item-side revenue measures at the requested grain."""
    required_columns = group_columns + [
        "order_id",
        "order_item_id",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ]
    missing_columns = [column for column in required_columns if column not in dataframe.columns]
    if missing_columns:
        missing_list = ", ".join(missing_columns)
        raise KeyError(f"Missing columns for revenue aggregation: {missing_list}")

    named_aggregations = {
        "order_item_count": ("order_item_id", "count"),
        "item_revenue": ("item_revenue", "sum"),
        "freight_value": ("freight_value", "sum"),
        "gross_merchandise_value": ("gross_merchandise_value", "sum"),
    }
    if include_order_count:
        named_aggregations["order_count"] = ("order_id", "nunique")

    grouped = (
        dataframe.groupby(group_columns, dropna=False)
        .agg(**named_aggregations)
        .reset_index()
    )

    metric_columns = ["item_revenue", "freight_value", "gross_merchandise_value"]
    grouped[metric_columns] = grouped[metric_columns].round(2)

    if include_order_count:
        ordered_columns = group_columns + [
            "order_count",
            "order_item_count",
            "item_revenue",
            "freight_value",
            "gross_merchandise_value",
        ]
        return grouped[ordered_columns]

    return grouped[
        group_columns
        + ["order_item_count", "item_revenue", "freight_value", "gross_merchandise_value"]
    ]


def summarize_payments(payments: pd.DataFrame) -> pd.DataFrame:
    """Summarize payment behavior without treating payments as sales grain."""
    payment_data = payments.copy()
    payment_data["payment_value"] = pd.to_numeric(
        payment_data["payment_value"], errors="coerce"
    ).fillna(0)

    summary = (
        payment_data.groupby("payment_type", dropna=False)
        .agg(
            payment_count=("payment_value", "count"),
            total_payment_value=("payment_value", "sum"),
            average_payment_value=("payment_value", "mean"),
        )
        .reset_index()
    )
    summary[["total_payment_value", "average_payment_value"]] = summary[
        ["total_payment_value", "average_payment_value"]
    ].round(2)
    return summary.sort_values("total_payment_value", ascending=False)


def build_kpi_overview(
    *,
    orders: pd.DataFrame,
    item_data: pd.DataFrame,
    payments: pd.DataFrame,
) -> pd.DataFrame:
    """Build a compact KPI overview from Silver tables."""
    item_revenue = round(float(item_data["item_revenue"].sum()), 2)
    freight_value = round(float(item_data["freight_value"].sum()), 2)
    gross_merchandise_value = round(float(item_data["gross_merchandise_value"].sum()), 2)
    order_count = int(orders["order_id"].nunique())
    item_order_count = int(item_data["order_id"].nunique())
    order_item_count = int(len(item_data))
    payment_value = round(float(pd.to_numeric(payments["payment_value"], errors="coerce").sum()), 2)

    rows = [
        {
            "metric_name": "distinct_orders",
            "metric_value": order_count,
            "metric_scope": "orders",
            "notes": "Distinct order_id count from the Silver orders table.",
        },
        {
            "metric_name": "orders_with_items",
            "metric_value": item_order_count,
            "metric_scope": "order_items",
            "notes": "Distinct order_id count represented in the Silver order_items table.",
        },
        {
            "metric_name": "order_item_count",
            "metric_value": order_item_count,
            "metric_scope": "order_items",
            "notes": "Row count at order item grain.",
        },
        {
            "metric_name": "item_revenue",
            "metric_value": item_revenue,
            "metric_scope": "order_items.price",
            "notes": "Sum of item price only; payments are not joined to item rows.",
        },
        {
            "metric_name": "freight_value",
            "metric_value": freight_value,
            "metric_scope": "order_items.freight_value",
            "notes": "Sum of item-level freight value.",
        },
        {
            "metric_name": "gross_merchandise_value",
            "metric_value": gross_merchandise_value,
            "metric_scope": "order_items.price + order_items.freight_value",
            "notes": "Item-side gross merchandise value before accounting adjustments.",
        },
        {
            "metric_name": "average_order_item_value",
            "metric_value": round(item_revenue / order_item_count, 2) if order_item_count else 0,
            "metric_scope": "order_items",
            "notes": "Item revenue divided by order item rows.",
        },
        {
            "metric_name": "payment_value_reported",
            "metric_value": payment_value,
            "metric_scope": "order_payments",
            "notes": "Reported payment value summarized separately from item-side revenue.",
        },
    ]

    return pd.DataFrame(rows)
