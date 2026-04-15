from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.gold.metrics import (  # noqa: E402
    add_item_revenue_measures,
    aggregate_item_revenue,
    summarize_payments,
)


def test_add_item_revenue_measures_uses_item_price_and_freight() -> None:
    dataframe = pd.DataFrame(
        {
            "price": ["10.00", "20.50"],
            "freight_value": ["1.25", "2.75"],
        }
    )

    result = add_item_revenue_measures(dataframe)

    assert result["item_revenue"].tolist() == [10.0, 20.5]
    assert result["gross_merchandise_value"].tolist() == [11.25, 23.25]


def test_aggregate_item_revenue_counts_distinct_orders_when_requested() -> None:
    dataframe = pd.DataFrame(
        {
            "order_status": ["delivered", "delivered", "canceled"],
            "order_id": ["o1", "o1", "o2"],
            "order_item_id": [1, 2, 1],
            "item_revenue": [10.0, 20.0, 30.0],
            "freight_value": [1.0, 2.0, 3.0],
            "gross_merchandise_value": [11.0, 22.0, 33.0],
        }
    )

    result = aggregate_item_revenue(
        dataframe,
        ["order_status"],
        include_order_count=True,
    ).sort_values("order_status")

    canceled = result[result["order_status"] == "canceled"].iloc[0]
    delivered = result[result["order_status"] == "delivered"].iloc[0]

    assert canceled["order_count"] == 1
    assert canceled["order_item_count"] == 1
    assert canceled["gross_merchandise_value"] == 33.0
    assert delivered["order_count"] == 1
    assert delivered["order_item_count"] == 2
    assert delivered["gross_merchandise_value"] == 33.0


def test_summarize_payments_keeps_payment_metrics_separate() -> None:
    payments = pd.DataFrame(
        {
            "payment_type": ["credit_card", "credit_card", "voucher"],
            "payment_value": [100.0, 50.0, 25.0],
        }
    )

    result = summarize_payments(payments).sort_values("payment_type")

    credit_card = result[result["payment_type"] == "credit_card"].iloc[0]
    voucher = result[result["payment_type"] == "voucher"].iloc[0]

    assert credit_card["payment_count"] == 2
    assert credit_card["total_payment_value"] == 150.0
    assert credit_card["average_payment_value"] == 75.0
    assert voucher["payment_count"] == 1
    assert voucher["total_payment_value"] == 25.0
