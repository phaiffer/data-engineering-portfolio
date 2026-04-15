from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from config import ApiConfig
from db import fetch_rows


MAX_LIMIT = 500
DEFAULT_MART_LIMIT = 50
DEFAULT_FACT_LIMIT = 25


class QueryValidationError(ValueError):
    """Raised when API query parameters are invalid."""


@dataclass(frozen=True)
class QueryResult:
    """Rows plus metadata for a list API response."""

    data: list[dict[str, Any]]
    filters: dict[str, Any]

    @property
    def row_count(self) -> int:
        """Return the number of rows in the response payload."""
        return len(self.data)


MART_COLUMNS: dict[str, tuple[str, ...]] = {
    "mart_daily_revenue": (
        "order_purchase_date",
        "order_status",
        "order_count",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_category_performance": (
        "product_category_name",
        "product_category_name_english",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_seller_performance": (
        "seller_id",
        "seller_state",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_customer_state_performance": (
        "customer_state",
        "order_count",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_order_status_summary": (
        "order_status",
        "order_count",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_payment_type_summary": (
        "payment_type",
        "payment_count",
        "total_payment_value",
        "average_payment_value",
    ),
    "fct_sales": (
        "order_id",
        "order_item_id",
        "product_id",
        "customer_id",
        "seller_id",
        "order_purchase_timestamp",
        "order_purchase_date",
        "order_status",
        "customer_state",
        "seller_state",
        "product_category_name",
        "product_category_name_english",
        "item_price",
        "freight_value",
        "gross_merchandise_value",
        "payment_value_total",
        "payment_record_count",
        "payment_installments_total",
        "payment_types_used",
    ),
}

SORTABLE_COLUMNS: dict[str, tuple[str, ...]] = {
    "mart_daily_revenue": (
        "order_purchase_date",
        "order_count",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_category_performance": (
        "product_category_name_english",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_seller_performance": (
        "seller_id",
        "seller_state",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "mart_customer_state_performance": (
        "customer_state",
        "order_count",
        "order_item_count",
        "item_revenue",
        "freight_value",
        "gross_merchandise_value",
    ),
    "fct_sales": (
        "order_purchase_date",
        "item_price",
        "freight_value",
        "gross_merchandise_value",
    ),
}

DEFAULT_SORTS: dict[str, tuple[str, str]] = {
    "mart_daily_revenue": ("order_purchase_date", "desc"),
    "mart_category_performance": ("gross_merchandise_value", "desc"),
    "mart_seller_performance": ("gross_merchandise_value", "desc"),
    "mart_customer_state_performance": ("gross_merchandise_value", "desc"),
    "fct_sales": ("order_purchase_date", "desc"),
}


def parse_limit(raw_limit: str | None, *, default: int, maximum: int = MAX_LIMIT) -> int:
    """Parse and validate a bounded limit query parameter."""
    if raw_limit is None or raw_limit == "":
        return default
    try:
        limit = int(raw_limit)
    except ValueError as exc:
        raise QueryValidationError("limit must be an integer.") from exc
    if limit < 1 or limit > maximum:
        raise QueryValidationError(f"limit must be between 1 and {maximum}.")
    return limit


def validate_sort_field(
    raw_sort_field: str | None,
    *,
    allowed_fields: tuple[str, ...],
    default: str,
) -> str:
    """Return a whitelisted sort field."""
    sort_field = raw_sort_field or default
    if sort_field not in allowed_fields:
        allowed = ", ".join(allowed_fields)
        raise QueryValidationError(f"sort_by must be one of: {allowed}.")
    return sort_field


def parse_sort_direction(raw_direction: str | None, *, default: str = "desc") -> str:
    """Parse a sort direction."""
    direction = (raw_direction or default).lower()
    if direction not in {"asc", "desc"}:
        raise QueryValidationError("sort must be either asc or desc.")
    return direction


def parse_min_float(raw_value: str | None, *, parameter_name: str) -> float | None:
    """Parse an optional minimum numeric filter."""
    if raw_value is None or raw_value == "":
        return None
    try:
        return float(raw_value)
    except ValueError as exc:
        raise QueryValidationError(f"{parameter_name} must be numeric.") from exc


def normalize_optional_text(raw_value: str | None) -> str | None:
    """Normalize an optional text filter."""
    if raw_value is None:
        return None
    normalized = raw_value.strip()
    return normalized or None


def _qualified_table(config: ApiConfig, table_name: str) -> str:
    return f'"{config.marts_schema}"."{table_name}"'


def _select_columns(table_name: str) -> str:
    return ", ".join(f'"{column}"' for column in MART_COLUMNS[table_name])


def _build_list_query(
    config: ApiConfig,
    *,
    table_name: str,
    where_clauses: list[str],
    parameters: list[Any],
    sort_by: str,
    sort_direction: str,
    limit: int,
) -> tuple[str, list[Any]]:
    sql = f"select {_select_columns(table_name)} from {_qualified_table(config, table_name)}"
    if where_clauses:
        sql += " where " + " and ".join(where_clauses)
    sql += f' order by "{sort_by}" {sort_direction}'
    sql += " limit ?"
    return sql, parameters + [limit]


def fetch_kpis(config: ApiConfig) -> dict[str, Any]:
    """Fetch dashboard-friendly KPIs from the modeled sales mart."""
    sql = f"""
        select
            count(distinct order_id) as total_orders,
            count(*) as total_order_items,
            sum(item_price) as total_item_revenue,
            sum(freight_value) as total_freight_value,
            sum(gross_merchandise_value) as total_gross_merchandise_value,
            sum(item_price) / nullif(count(distinct order_id), 0) as average_order_value_item_side
        from {_qualified_table(config, 'fct_sales')}
    """
    rows = fetch_rows(config, sql)
    return rows[0] if rows else {}


def fetch_daily_revenue(
    config: ApiConfig,
    *,
    limit: int,
    order_status: str | None,
    sort_direction: str,
) -> QueryResult:
    """Fetch rows from mart_daily_revenue."""
    filters: dict[str, Any] = {
        "limit": limit,
        "order_status": order_status,
        "sort": sort_direction,
    }
    where_clauses: list[str] = []
    parameters: list[Any] = []

    if order_status:
        where_clauses.append("order_status = ?")
        parameters.append(order_status)

    sql, query_parameters = _build_list_query(
        config,
        table_name="mart_daily_revenue",
        where_clauses=where_clauses,
        parameters=parameters,
        sort_by="order_purchase_date",
        sort_direction=sort_direction,
        limit=limit,
    )
    return QueryResult(fetch_rows(config, sql, query_parameters), filters)


def fetch_category_performance(
    config: ApiConfig,
    *,
    limit: int,
    sort_by: str,
    sort_direction: str,
    min_item_revenue: float | None,
) -> QueryResult:
    """Fetch rows from mart_category_performance."""
    filters: dict[str, Any] = {
        "limit": limit,
        "sort_by": sort_by,
        "sort": sort_direction,
        "min_item_revenue": min_item_revenue,
    }
    where_clauses: list[str] = []
    parameters: list[Any] = []
    if min_item_revenue is not None:
        where_clauses.append("item_revenue >= ?")
        parameters.append(min_item_revenue)

    sql, query_parameters = _build_list_query(
        config,
        table_name="mart_category_performance",
        where_clauses=where_clauses,
        parameters=parameters,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit,
    )
    return QueryResult(fetch_rows(config, sql, query_parameters), filters)


def fetch_seller_performance(
    config: ApiConfig,
    *,
    limit: int,
    seller_state: str | None,
    sort_by: str,
    sort_direction: str,
) -> QueryResult:
    """Fetch rows from mart_seller_performance."""
    filters: dict[str, Any] = {
        "limit": limit,
        "seller_state": seller_state,
        "sort_by": sort_by,
        "sort": sort_direction,
    }
    where_clauses: list[str] = []
    parameters: list[Any] = []
    if seller_state:
        where_clauses.append("seller_state = ?")
        parameters.append(seller_state.upper())

    sql, query_parameters = _build_list_query(
        config,
        table_name="mart_seller_performance",
        where_clauses=where_clauses,
        parameters=parameters,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit,
    )
    return QueryResult(fetch_rows(config, sql, query_parameters), filters)


def fetch_customer_state_performance(
    config: ApiConfig,
    *,
    limit: int,
    customer_state: str | None,
    sort_by: str,
    sort_direction: str,
) -> QueryResult:
    """Fetch rows from mart_customer_state_performance."""
    filters: dict[str, Any] = {
        "limit": limit,
        "customer_state": customer_state,
        "sort_by": sort_by,
        "sort": sort_direction,
    }
    where_clauses: list[str] = []
    parameters: list[Any] = []
    if customer_state:
        where_clauses.append("customer_state = ?")
        parameters.append(customer_state.upper())

    sql, query_parameters = _build_list_query(
        config,
        table_name="mart_customer_state_performance",
        where_clauses=where_clauses,
        parameters=parameters,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit,
    )
    return QueryResult(fetch_rows(config, sql, query_parameters), filters)


def fetch_simple_mart(config: ApiConfig, table_name: str, order_by: str) -> QueryResult:
    """Fetch all rows from a small summary mart."""
    sql = (
        f"select {_select_columns(table_name)} "
        f"from {_qualified_table(config, table_name)} "
        f'order by "{order_by}" desc'
    )
    return QueryResult(fetch_rows(config, sql), {"sort_by": order_by, "sort": "desc"})


def fetch_fct_sales_sample(
    config: ApiConfig,
    *,
    limit: int,
    order_status: str | None,
    customer_state: str | None,
    seller_state: str | None,
    category: str | None,
    sort_by: str,
    sort_direction: str,
) -> QueryResult:
    """Fetch a small sample from fct_sales for exploration."""
    filters: dict[str, Any] = {
        "limit": limit,
        "order_status": order_status,
        "customer_state": customer_state,
        "seller_state": seller_state,
        "category": category,
        "sort_by": sort_by,
        "sort": sort_direction,
    }
    where_clauses: list[str] = []
    parameters: list[Any] = []

    if order_status:
        where_clauses.append("order_status = ?")
        parameters.append(order_status)
    if customer_state:
        where_clauses.append("customer_state = ?")
        parameters.append(customer_state.upper())
    if seller_state:
        where_clauses.append("seller_state = ?")
        parameters.append(seller_state.upper())
    if category:
        where_clauses.append(
            "(product_category_name = ? or product_category_name_english = ?)"
        )
        parameters.extend([category, category])

    sql, query_parameters = _build_list_query(
        config,
        table_name="fct_sales",
        where_clauses=where_clauses,
        parameters=parameters,
        sort_by=sort_by,
        sort_direction=sort_direction,
        limit=limit,
    )
    return QueryResult(fetch_rows(config, sql, query_parameters), filters)
