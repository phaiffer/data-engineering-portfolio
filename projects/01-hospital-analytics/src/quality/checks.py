from __future__ import annotations

from typing import Any, Sequence

import pandas as pd


def validate_expected_columns(
    dataframe: pd.DataFrame, expected_columns: Sequence[str]
) -> dict[str, Any]:
    """Validate that the DataFrame contains the expected Silver columns."""
    actual_columns = list(dataframe.columns)
    missing_columns = [
        column for column in expected_columns if column not in actual_columns
    ]
    unexpected_columns = [
        column for column in actual_columns if column not in expected_columns
    ]

    return {
        "passed": not missing_columns and not unexpected_columns,
        "expected_columns": list(expected_columns),
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
    }


def validate_required_columns(
    dataframe: pd.DataFrame, required_columns: Sequence[str]
) -> dict[str, Any]:
    """Validate that required structural Silver columns are present."""
    missing_columns = [
        column for column in required_columns if column not in dataframe.columns
    ]

    return {
        "passed": not missing_columns,
        "required_columns": list(required_columns),
        "missing_columns": missing_columns,
    }


def validate_row_count_preserved(
    bronze_dataframe: pd.DataFrame, silver_dataframe: pd.DataFrame
) -> dict[str, Any]:
    """Validate that Silver preserves the Bronze row count."""
    input_rows = int(len(bronze_dataframe))
    output_rows = int(len(silver_dataframe))

    return {
        "passed": input_rows == output_rows,
        "input_rows": input_rows,
        "output_rows": output_rows,
        "row_count_difference": output_rows - input_rows,
    }


def summarize_duplicate_rows(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Return a duplicate row count for the provided DataFrame."""
    duplicate_row_count = int(dataframe.duplicated().sum())

    return {
        "duplicate_row_count": duplicate_row_count,
    }


def summarize_numeric_conversions(
    bronze_dataframe: pd.DataFrame,
    silver_dataframe: pd.DataFrame,
    numeric_columns: Sequence[str],
) -> dict[str, Any]:
    """
    Summarize numeric conversion results after Silver type casting.

    Invalid parsed values are counted as source non-null values that became null in
    the Silver numeric column.
    """
    summary: dict[str, Any] = {}

    for column in numeric_columns:
        if column not in silver_dataframe.columns:
            summary[column] = {"column_missing": True}
            continue

        source_values = (
            bronze_dataframe[column]
            if column in bronze_dataframe.columns
            else silver_dataframe[column]
        )
        source_non_null_count = int(source_values.notna().sum())
        silver_null_count = int(silver_dataframe[column].isna().sum())
        invalid_conversion_count = int(
            (source_values.notna() & silver_dataframe[column].isna()).sum()
        )

        summary[column] = {
            "column_missing": False,
            "source_non_null_count": source_non_null_count,
            "silver_null_count": silver_null_count,
            "invalid_conversion_count": invalid_conversion_count,
            "silver_dtype": str(silver_dataframe[column].dtype),
        }

    return summary


def summarize_nulls(
    dataframe: pd.DataFrame, columns: Sequence[str] | None = None
) -> dict[str, int]:
    """Return null counts for selected columns or all DataFrame columns."""
    selected_columns = list(columns) if columns is not None else list(dataframe.columns)
    return {
        column: int(dataframe[column].isna().sum())
        for column in selected_columns
        if column in dataframe.columns
    }


def validate_silver_dataframe(
    bronze_dataframe: pd.DataFrame,
    silver_dataframe: pd.DataFrame,
    expected_columns: Sequence[str],
    required_columns: Sequence[str],
    numeric_columns: Sequence[str],
) -> dict[str, Any]:
    """Run lightweight reusable validation checks for Silver v1."""
    checks = {
        "expected_columns": validate_expected_columns(
            silver_dataframe, expected_columns
        ),
        "required_columns": validate_required_columns(
            silver_dataframe, required_columns
        ),
        "row_count_preserved": validate_row_count_preserved(
            bronze_dataframe, silver_dataframe
        ),
        "duplicates": summarize_duplicate_rows(silver_dataframe),
        "numeric_conversions": summarize_numeric_conversions(
            bronze_dataframe=bronze_dataframe,
            silver_dataframe=silver_dataframe,
            numeric_columns=numeric_columns,
        ),
        "key_null_counts": summarize_nulls(
            silver_dataframe,
            columns=[
                "department_referral",
                "patient_satisfaction_score",
                "patient_admission_timestamp",
            ],
        ),
    }

    return {
        "passed": all(
            check.get("passed", True)
            for check in checks.values()
            if isinstance(check, dict)
        ),
        "checks": checks,
    }


def run_quality_checks() -> None:
    """Placeholder for broader project-level quality orchestration."""
    raise NotImplementedError("Use validate_silver_dataframe for Silver v1 checks.")
