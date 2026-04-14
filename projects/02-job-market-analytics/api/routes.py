from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from db import (
    MART_COLUMNS,
    DatabaseQueryError,
    check_database_connection,
    fetch_dashboard_kpis,
    fetch_mart_rows,
)


api_bp = Blueprint("api", __name__)

MAX_LIMIT = 1000


def parse_limit(default: int | None = None) -> tuple[int | None, str | None]:
    """Parse and validate the optional limit query parameter."""
    raw_limit = request.args.get("limit")
    if raw_limit is None:
        return default, None
    try:
        limit = int(raw_limit)
    except ValueError:
        return None, "limit must be an integer."
    if limit < 1 or limit > MAX_LIMIT:
        return None, f"limit must be between 1 and {MAX_LIMIT}."
    return limit, None


def parse_order_by(mart_name: str) -> tuple[str | None, str | None]:
    """Parse and validate the optional order_by query parameter."""
    order_by = request.args.get("order_by")
    if order_by is None:
        return None, None
    if order_by not in MART_COLUMNS[mart_name]:
        allowed_columns = ", ".join(MART_COLUMNS[mart_name])
        return None, f"order_by must be one of: {allowed_columns}."
    return order_by, None


def parse_direction() -> tuple[bool, str | None]:
    """Parse the optional sort direction query parameter."""
    direction = request.args.get("direction", "desc").lower()
    if direction not in {"asc", "desc"}:
        return True, "direction must be either asc or desc."
    return direction == "desc", None


def query_mart(mart_name: str, default_order_by: str, default_limit: int | None = None):
    """Return JSON data for a whitelisted DBT mart."""
    limit, limit_error = parse_limit(default=default_limit)
    if limit_error:
        return jsonify({"error": {"message": limit_error}}), 400

    order_by, order_error = parse_order_by(mart_name)
    if order_error:
        return jsonify({"error": {"message": order_error}}), 400

    descending, direction_error = parse_direction()
    if direction_error:
        return jsonify({"error": {"message": direction_error}}), 400

    rows = fetch_mart_rows(
        config=current_app.config["API_CONFIG"],
        mart_name=mart_name,
        order_by=order_by or default_order_by,
        limit=limit,
        descending=descending,
    )
    return jsonify({"data": rows})


@api_bp.get("/health")
def health():
    """Return service health and a lightweight PostgreSQL connectivity check."""
    config = current_app.config["API_CONFIG"]
    try:
        database_ok = check_database_connection(config)
    except DatabaseQueryError:
        database_ok = False

    status_code = 200 if database_ok else 503
    status = "ok" if database_ok else "degraded"

    return (
        jsonify(
            {
                "data": {
                    "service": config.service_name,
                    "status": status,
                    "database": "ok" if database_ok else "unavailable",
                    "source": f"{config.marts_schema} DBT schema over PostgreSQL",
                }
            }
        ),
        status_code,
    )


@api_bp.get("/api/v1/job-titles")
def job_titles():
    """Return job-title summary rows from the DBT mart."""
    return query_mart("mart_job_title_summary", "average_salary_usd", default_limit=10)


@api_bp.get("/api/v1/industries")
def industries():
    """Return industry summary rows from the DBT mart."""
    return query_mart("mart_industry_summary", "total_records")


@api_bp.get("/api/v1/locations")
def locations():
    """Return location summary rows from the DBT mart."""
    return query_mart("mart_location_summary", "average_salary_usd", default_limit=10)


@api_bp.get("/api/v1/automation-ai")
def automation_ai():
    """Return automation-risk and AI-adoption summary rows from the DBT mart."""
    return query_mart("mart_automation_ai_summary", "total_records")


@api_bp.get("/api/v1/job-title-summary")
def job_title_summary():
    """Return job-title summary rows using the first dashboard API alias."""
    return query_mart("mart_job_title_summary", "average_salary_usd", default_limit=10)


@api_bp.get("/api/v1/industry-summary")
def industry_summary():
    """Return industry summary rows using the first dashboard API alias."""
    return query_mart("mart_industry_summary", "total_records")


@api_bp.get("/api/v1/location-summary")
def location_summary():
    """Return location summary rows using the first dashboard API alias."""
    return query_mart("mart_location_summary", "average_salary_usd", default_limit=10)


@api_bp.get("/api/v1/automation-ai-summary")
def automation_ai_summary():
    """Return automation-risk and AI-adoption summary rows using the first dashboard API alias."""
    return query_mart("mart_automation_ai_summary", "total_records")


@api_bp.get("/api/v1/kpis")
def kpis():
    """Return dashboard KPIs derived from the PostgreSQL Silver table."""
    return jsonify({"data": fetch_dashboard_kpis(current_app.config["API_CONFIG"])})

