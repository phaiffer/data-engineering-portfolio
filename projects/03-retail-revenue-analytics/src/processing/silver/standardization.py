from __future__ import annotations

import re
from typing import Iterable

import pandas as pd


def normalize_column_name(column_name: str) -> str:
    """Normalize a source column name to lowercase snake_case."""
    normalized = column_name.strip()
    normalized = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", normalized)
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized)
    return normalized.strip("_").lower()


def normalize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the dataframe with normalized column names."""
    normalized = dataframe.copy()
    normalized.columns = [normalize_column_name(column) for column in normalized.columns]
    return normalized


def standardize_text_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Trim whitespace from text columns and convert blank strings to nulls.

    This keeps source values intact while handling common CSV whitespace noise.
    """
    standardized = dataframe.copy()
    text_columns = standardized.select_dtypes(include=["object", "string"]).columns

    for column in text_columns:
        standardized[column] = standardized[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
        standardized[column] = standardized[column].replace("", pd.NA)

    return standardized


def parse_datetime_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Parse configured datetime columns when present."""
    parsed = dataframe.copy()

    for column in columns:
        if column in parsed.columns:
            parsed[column] = pd.to_datetime(parsed[column], errors="coerce")

    return parsed


def parse_numeric_columns(dataframe: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    """Parse configured numeric columns when present."""
    parsed = dataframe.copy()

    for column in columns:
        if column in parsed.columns:
            parsed[column] = pd.to_numeric(parsed[column], errors="coerce")

    return parsed


def standardize_source_table(
    dataframe: pd.DataFrame,
    *,
    datetime_columns: Iterable[str] = (),
    numeric_columns: Iterable[str] = (),
) -> pd.DataFrame:
    """
    Apply safe source-aligned Silver standardization.

    The function preserves row grain and does not join, aggregate, deduplicate,
    or create business keys.
    """
    standardized = normalize_column_names(dataframe)
    standardized = standardize_text_values(standardized)
    standardized = parse_datetime_columns(standardized, datetime_columns)
    standardized = parse_numeric_columns(standardized, numeric_columns)
    return standardized
