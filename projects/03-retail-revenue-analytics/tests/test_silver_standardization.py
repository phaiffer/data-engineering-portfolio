from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from processing.silver.standardization import (  # noqa: E402
    normalize_column_name,
    standardize_source_table,
    standardize_text_values,
)


def test_normalize_column_name_returns_lowercase_snake_case() -> None:
    assert normalize_column_name(" Order Purchase Timestamp ") == "order_purchase_timestamp"
    assert normalize_column_name("ProductCategoryName") == "product_category_name"
    assert normalize_column_name("seller-state") == "seller_state"


def test_standardize_text_values_trims_and_converts_blanks_to_null() -> None:
    dataframe = pd.DataFrame(
        {
            "name": ["  books  ", "   ", None],
            "value": [1, 2, 3],
        }
    )

    result = standardize_text_values(dataframe)

    assert result.loc[0, "name"] == "books"
    assert pd.isna(result.loc[1, "name"])
    assert pd.isna(result.loc[2, "name"])
    assert result["value"].tolist() == [1, 2, 3]


def test_standardize_source_table_parses_configured_types() -> None:
    dataframe = pd.DataFrame(
        {
            "Order Purchase Timestamp": ["2018-01-01 10:00:00", "not a date"],
            "Price": ["10.50", "bad value"],
        }
    )

    result = standardize_source_table(
        dataframe,
        datetime_columns=("order_purchase_timestamp",),
        numeric_columns=("price",),
    )

    assert list(result.columns) == ["order_purchase_timestamp", "price"]
    assert str(result["order_purchase_timestamp"].dtype).startswith("datetime64")
    assert result.loc[0, "price"] == 10.5
    assert pd.isna(result.loc[1, "price"])
