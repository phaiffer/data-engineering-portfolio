from __future__ import annotations

import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


PROJECT_API = Path(__file__).resolve().parents[1] / "api"
if str(PROJECT_API) not in sys.path:
    sys.path.insert(0, str(PROJECT_API))

from serializers import serialize_row, serialize_rows, serialize_value  # noqa: E402


def test_serialize_value_handles_dates_and_decimals() -> None:
    assert serialize_value(date(2026, 4, 15)) == "2026-04-15"
    assert serialize_value(datetime(2026, 4, 15, 10, 30)) == "2026-04-15T10:30:00"
    assert serialize_value(Decimal("12.34")) == 12.34
    assert serialize_value(None) is None


def test_serialize_row_converts_json_friendly_values() -> None:
    row = {
        "order_purchase_date": date(2026, 4, 15),
        "gross_merchandise_value": Decimal("99.90"),
        "order_status": "delivered",
    }

    assert serialize_row(row) == {
        "order_purchase_date": "2026-04-15",
        "gross_merchandise_value": 99.9,
        "order_status": "delivered",
    }


def test_serialize_rows_maps_all_rows() -> None:
    rows = [{"value": Decimal("1.5")}, {"value": Decimal("2.5")}]

    assert serialize_rows(rows) == [{"value": 1.5}, {"value": 2.5}]
