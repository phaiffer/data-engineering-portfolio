from __future__ import annotations

import sys
from pathlib import Path


PROJECT_API = Path(__file__).resolve().parents[1] / "api"
if str(PROJECT_API) not in sys.path:
    sys.path.insert(0, str(PROJECT_API))

from queries import (  # noqa: E402
    QueryValidationError,
    normalize_optional_text,
    parse_limit,
    parse_min_float,
    parse_sort_direction,
    validate_sort_field,
)


def assert_raises(expected_error: type[Exception], message_fragment: str, func, *args, **kwargs) -> None:
    """Assert that a callable raises an expected error with a useful message."""
    try:
        func(*args, **kwargs)
    except expected_error as exc:
        assert message_fragment in str(exc)
        return

    raise AssertionError(f"Expected {expected_error.__name__} to be raised.")


def test_parse_limit_uses_default_and_accepts_valid_integer() -> None:
    assert parse_limit(None, default=50) == 50
    assert parse_limit("10", default=50) == 10


def test_parse_limit_rejects_invalid_values() -> None:
    assert_raises(QueryValidationError, "integer", parse_limit, "abc", default=50)
    assert_raises(QueryValidationError, "between", parse_limit, "0", default=50)
    assert_raises(QueryValidationError, "between", parse_limit, "501", default=50, maximum=500)


def test_validate_sort_field_uses_whitelist() -> None:
    allowed = ("gross_merchandise_value", "item_revenue")

    assert (
        validate_sort_field(None, allowed_fields=allowed, default="gross_merchandise_value")
        == "gross_merchandise_value"
    )
    assert validate_sort_field("item_revenue", allowed_fields=allowed, default="gross_merchandise_value") == "item_revenue"

    assert_raises(
        QueryValidationError,
        "sort_by",
        validate_sort_field,
        "drop table",
        allowed_fields=allowed,
        default="gross_merchandise_value",
    )


def test_parse_sort_direction_accepts_only_asc_or_desc() -> None:
    assert parse_sort_direction(None, default="desc") == "desc"
    assert parse_sort_direction("ASC") == "asc"

    assert_raises(QueryValidationError, "sort", parse_sort_direction, "sideways")


def test_parse_min_float_and_optional_text_helpers() -> None:
    assert parse_min_float(None, parameter_name="min_item_revenue") is None
    assert parse_min_float("10.5", parameter_name="min_item_revenue") == 10.5
    assert normalize_optional_text(" SP ") == "SP"
    assert normalize_optional_text("   ") is None

    assert_raises(
        QueryValidationError,
        "numeric",
        parse_min_float,
        "large",
        parameter_name="min_item_revenue",
    )
