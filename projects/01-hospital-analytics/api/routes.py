from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from db import VIEW_COLUMNS, fetch_one, fetch_rows


api_bp = Blueprint("api", __name__)

MAX_LIMIT = 1000


def parse_limit() -> tuple[int | None, str | None]:
    """Parse and validate the optional limit query parameter."""
    raw_limit = request.args.get("limit")
    if raw_limit is None:
        return None, None
    try:
        limit = int(raw_limit)
    except ValueError:
        return None, "limit must be an integer."
    if limit < 1 or limit > MAX_LIMIT:
        return None, f"limit must be between 1 and {MAX_LIMIT}."
    return limit, None


def parse_order_by(view_name: str) -> tuple[str | None, str | None]:
    """Parse and validate the optional order_by query parameter."""
    order_by = request.args.get("order_by")
    if order_by is None:
        return None, None
    if order_by not in VIEW_COLUMNS[view_name]:
        allowed_columns = ", ".join(VIEW_COLUMNS[view_name])
        return None, f"order_by must be one of: {allowed_columns}."
    return order_by, None


def query_view(view_name: str):
    """Return JSON data for a serving view with safe optional parameters."""
    limit, limit_error = parse_limit()
    if limit_error:
        return jsonify({"error": {"message": limit_error}}), 400

    order_by, order_error = parse_order_by(view_name)
    if order_error:
        return jsonify({"error": {"message": order_error}}), 400

    rows = fetch_rows(
        config=current_app.config["API_CONFIG"],
        view_name=view_name,
        order_by=order_by,
        limit=limit,
    )
    return jsonify({"data": rows})


@api_bp.get("/health")
def health():
    """Return a simple service health response."""
    config = current_app.config["API_CONFIG"]
    return jsonify({"data": {"service": config.service_name, "status": "ok"}})


@api_bp.get("/api/v1/kpis")
def kpis():
    """Return the single-row dashboard KPI view."""
    row = fetch_one(
        config=current_app.config["API_CONFIG"],
        view_name="v_dashboard_kpis",
    )
    return jsonify({"data": row or {}})


@api_bp.get("/api/v1/daily-patient-flow")
def daily_patient_flow():
    """Return daily patient flow rows from the serving view."""
    return query_view("v_daily_patient_flow")


@api_bp.get("/api/v1/department-referrals")
def department_referrals():
    """Return department referral summary rows from the serving view."""
    return query_view("v_department_referral_summary")


@api_bp.get("/api/v1/demographics")
def demographics():
    """Return demographic summary rows from the serving view."""
    return query_view("v_demographic_summary")
