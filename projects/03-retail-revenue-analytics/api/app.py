from __future__ import annotations

import logging
from urllib.parse import urlparse

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from config import load_config
from db import DatabaseQueryError, DatabaseUnavailableError, check_database
from queries import (
    DEFAULT_FACT_LIMIT,
    DEFAULT_MART_LIMIT,
    DEFAULT_SORTS,
    SORTABLE_COLUMNS,
    QueryResult,
    QueryValidationError,
    fetch_category_performance,
    fetch_customer_state_performance,
    fetch_daily_revenue,
    fetch_fct_sales_sample,
    fetch_kpis,
    fetch_seller_performance,
    fetch_simple_mart,
    normalize_optional_text,
    parse_limit,
    parse_min_float,
    parse_sort_direction,
    validate_sort_field,
)


LOCAL_DEV_CORS_PORT_MIN = 5173
LOCAL_DEV_CORS_PORT_MAX = 5199
LOCAL_DEV_CORS_HOSTS = {"127.0.0.1", "localhost"}


def _list_response(result: QueryResult):
    return jsonify(
        {
            "data": result.data,
            "row_count": result.row_count,
            "filters": result.filters,
        }
    )


def _api_index_payload() -> dict[str, object]:
    return {
        "project": "retail-revenue-analytics",
        "api_layer": "read-only Flask API over DuckDB DBT marts",
        "endpoints": {
            "health": "/health",
            "index": "/api/v1",
            "kpis": "/api/v1/kpis",
            "daily_revenue": "/api/v1/daily-revenue",
            "category_performance": "/api/v1/category-performance",
            "seller_performance": "/api/v1/seller-performance",
            "customer_state_performance": "/api/v1/customer-state-performance",
            "order_status_summary": "/api/v1/order-status-summary",
            "payment_type_summary": "/api/v1/payment-type-summary",
            "fct_sales_sample": "/api/v1/fct-sales",
        },
        "notes": [
            "The API reads modeled DuckDB marts and does not rebuild transformation logic.",
            "Item-side revenue measures are analytical and not accounting-grade.",
            "Payment summaries describe payment behavior, not item-level sales revenue.",
        ],
    }


def _is_local_dev_origin(origin: str) -> bool:
    """Return true for HTTP Vite-style localhost origins in local development."""
    parsed = urlparse(origin)
    if parsed.scheme != "http":
        return False
    if parsed.hostname not in LOCAL_DEV_CORS_HOSTS:
        return False
    if parsed.port is None:
        return False
    return LOCAL_DEV_CORS_PORT_MIN <= parsed.port <= LOCAL_DEV_CORS_PORT_MAX


def _is_allowed_cors_origin(origin: str | None, api_config) -> bool:
    if not origin:
        return False
    if origin in api_config.cors_allowed_origins:
        return True
    return api_config.allow_local_dev_cors and _is_local_dev_origin(origin)


def create_app() -> Flask:
    """Create and configure the local retail revenue analytics API."""
    app = Flask(__name__)
    app.config["API_CONFIG"] = load_config()

    logging.basicConfig(level=logging.INFO)

    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get("Origin")
        api_config = app.config["API_CONFIG"]
        if _is_allowed_cors_origin(origin, api_config):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "600"
        return response

    @app.get("/health")
    def health():
        """Return API health and the expected DuckDB mart database state."""
        config = app.config["API_CONFIG"]
        database_exists = config.duckdb_path.exists()
        database_ok = False
        if database_exists:
            try:
                database_ok = check_database(config)
            except (DatabaseQueryError, DatabaseUnavailableError):
                database_ok = False

        status_code = 200 if database_ok else 503
        return (
            jsonify(
                {
                    "status": "ok" if database_ok else "degraded",
                    "project": "retail-revenue-analytics",
                    "api_layer": "read-only Flask API over DuckDB DBT marts",
                    "database_path": str(config.duckdb_path),
                    "database_exists": database_exists,
                }
            ),
            status_code,
        )

    @app.get("/api/v1")
    def api_index():
        """Return a concise index of available API endpoints."""
        return jsonify(_api_index_payload())

    @app.get("/api/v1/kpis")
    def kpis():
        """Return dashboard-friendly KPIs from the sales mart."""
        return jsonify(
            {
                "data": fetch_kpis(app.config["API_CONFIG"]),
                "notes": [
                    "KPIs use item-side measures from the modeled fct_sales mart.",
                    "total_item_revenue is the sum of item_price.",
                    "total_gross_merchandise_value is item_price plus freight_value.",
                    "These are analytical measures, not accounting-grade revenue.",
                ],
            }
        )

    @app.get("/api/v1/daily-revenue")
    def daily_revenue():
        """Return daily revenue rows from mart_daily_revenue."""
        limit = parse_limit(request.args.get("limit"), default=DEFAULT_MART_LIMIT)
        sort_direction = parse_sort_direction(request.args.get("sort"), default="desc")
        result = fetch_daily_revenue(
            app.config["API_CONFIG"],
            limit=limit,
            order_status=normalize_optional_text(request.args.get("order_status")),
            sort_direction=sort_direction,
        )
        return _list_response(result)

    @app.get("/api/v1/category-performance")
    def category_performance():
        """Return category performance rows from mart_category_performance."""
        table_name = "mart_category_performance"
        default_sort, default_direction = DEFAULT_SORTS[table_name]
        limit = parse_limit(request.args.get("limit"), default=DEFAULT_MART_LIMIT)
        sort_by = validate_sort_field(
            request.args.get("sort_by"),
            allowed_fields=SORTABLE_COLUMNS[table_name],
            default=default_sort,
        )
        sort_direction = parse_sort_direction(request.args.get("sort"), default=default_direction)
        min_item_revenue = parse_min_float(
            request.args.get("min_item_revenue"),
            parameter_name="min_item_revenue",
        )
        return _list_response(
            fetch_category_performance(
                app.config["API_CONFIG"],
                limit=limit,
                sort_by=sort_by,
                sort_direction=sort_direction,
                min_item_revenue=min_item_revenue,
            )
        )

    @app.get("/api/v1/seller-performance")
    def seller_performance():
        """Return seller performance rows from mart_seller_performance."""
        table_name = "mart_seller_performance"
        default_sort, default_direction = DEFAULT_SORTS[table_name]
        limit = parse_limit(request.args.get("limit"), default=DEFAULT_MART_LIMIT)
        sort_by = validate_sort_field(
            request.args.get("sort_by"),
            allowed_fields=SORTABLE_COLUMNS[table_name],
            default=default_sort,
        )
        sort_direction = parse_sort_direction(request.args.get("sort"), default=default_direction)
        return _list_response(
            fetch_seller_performance(
                app.config["API_CONFIG"],
                limit=limit,
                seller_state=normalize_optional_text(request.args.get("seller_state")),
                sort_by=sort_by,
                sort_direction=sort_direction,
            )
        )

    @app.get("/api/v1/customer-state-performance")
    def customer_state_performance():
        """Return customer state performance rows."""
        table_name = "mart_customer_state_performance"
        default_sort, default_direction = DEFAULT_SORTS[table_name]
        limit = parse_limit(request.args.get("limit"), default=DEFAULT_MART_LIMIT)
        sort_by = validate_sort_field(
            request.args.get("sort_by"),
            allowed_fields=SORTABLE_COLUMNS[table_name],
            default=default_sort,
        )
        sort_direction = parse_sort_direction(request.args.get("sort"), default=default_direction)
        return _list_response(
            fetch_customer_state_performance(
                app.config["API_CONFIG"],
                limit=limit,
                customer_state=normalize_optional_text(request.args.get("customer_state")),
                sort_by=sort_by,
                sort_direction=sort_direction,
            )
        )

    @app.get("/api/v1/order-status-summary")
    def order_status_summary():
        """Return order status summary rows."""
        return _list_response(
            fetch_simple_mart(
                app.config["API_CONFIG"],
                "mart_order_status_summary",
                "gross_merchandise_value",
            )
        )

    @app.get("/api/v1/payment-type-summary")
    def payment_type_summary():
        """Return payment type summary rows."""
        return _list_response(
            fetch_simple_mart(
                app.config["API_CONFIG"],
                "mart_payment_type_summary",
                "total_payment_value",
            )
        )

    @app.get("/api/v1/fct-sales")
    def fct_sales_sample():
        """Return a small exploratory sample from fct_sales."""
        table_name = "fct_sales"
        default_sort, default_direction = DEFAULT_SORTS[table_name]
        limit = parse_limit(request.args.get("limit"), default=DEFAULT_FACT_LIMIT, maximum=100)
        sort_by = validate_sort_field(
            request.args.get("sort_by"),
            allowed_fields=SORTABLE_COLUMNS[table_name],
            default=default_sort,
        )
        sort_direction = parse_sort_direction(request.args.get("sort"), default=default_direction)
        return _list_response(
            fetch_fct_sales_sample(
                app.config["API_CONFIG"],
                limit=limit,
                order_status=normalize_optional_text(request.args.get("order_status")),
                customer_state=normalize_optional_text(request.args.get("customer_state")),
                seller_state=normalize_optional_text(request.args.get("seller_state")),
                category=normalize_optional_text(request.args.get("category")),
                sort_by=sort_by,
                sort_direction=sort_direction,
            )
        )

    @app.errorhandler(QueryValidationError)
    def handle_query_validation_error(error):
        return jsonify({"error": "invalid_request", "message": str(error)}), 400

    @app.errorhandler(DatabaseUnavailableError)
    def handle_database_unavailable(error):
        return (
            jsonify(
                {
                    "error": "database_unavailable",
                    "message": "The DuckDB mart database file is missing.",
                    "details": str(error),
                }
            ),
            503,
        )

    @app.errorhandler(DatabaseQueryError)
    def handle_database_error(error):
        app.logger.exception("Database query failed: %s", error)
        return (
            jsonify(
                {
                    "error": "database_query_failed",
                    "message": "The API could not read from the DuckDB mart layer.",
                }
            ),
            503,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"error": "http_error", "message": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unexpected API error: %s", error)
        return jsonify({"error": "unexpected_error", "message": "Unexpected API error."}), 500

    return app


if __name__ == "__main__":
    flask_app = create_app()
    api_config = flask_app.config["API_CONFIG"]
    flask_app.run(
        host=api_config.host,
        port=api_config.port,
        debug=api_config.debug,
    )
