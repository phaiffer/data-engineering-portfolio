from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import (
    get_project_root,
    get_raw_data_dir,
    list_supported_data_files,
    path_relative_to_project,
)
from processing.bronze.profiling import select_main_csv_file


RAW_TO_SILVER_COLUMN_MAPPING = {
    "Patient Id": "patient_id",
    "Patient Admission Date": "patient_admission_date",
    "Patient Admission Time": "patient_admission_time",
    "Merged": "merged_raw_value",
    "Patient Gender": "patient_gender",
    "Patient Age": "patient_age",
    "Patient Race": "patient_race",
    "Department Referral": "department_referral",
    "Patient Admission Flag": "patient_admission_flag",
    "Patient Satisfaction Score": "patient_satisfaction_score",
    "Patient Waittime": "patient_waittime",
}

SILVER_OUTPUT_FILENAME = "healthcare_analytics_patient_flow_silver.csv"
SILVER_METADATA_FILENAME = "healthcare_analytics_patient_flow_silver_metadata.json"
NUMERIC_COLUMNS = ("patient_age", "patient_satisfaction_score", "patient_waittime")
SILVER_COLUMNS = [
    *RAW_TO_SILVER_COLUMN_MAPPING.values(),
    "patient_admission_timestamp",
    "silver_loaded_at_utc",
]


def get_silver_data_dir() -> Path:
    """Return the local Silver output directory for the project."""
    return get_project_root() / "data" / "silver"


def get_default_silver_output_path() -> Path:
    """Return the default local Silver CSV artifact path."""
    return get_silver_data_dir() / SILVER_OUTPUT_FILENAME


def get_default_silver_metadata_path() -> Path:
    """Return the default local Silver metadata artifact path."""
    return get_silver_data_dir() / SILVER_METADATA_FILENAME


def resolve_main_bronze_csv(raw_data_dir: Path | None = None) -> Path:
    """Resolve the main Bronze CSV using the same deterministic rule as Bronze."""
    raw_dir = raw_data_dir or get_raw_data_dir()
    csv_files = list_supported_data_files(raw_dir)
    return select_main_csv_file(csv_files)


def load_bronze_csv(csv_path: Path) -> pd.DataFrame:
    """Load the Bronze CSV with raw columns preserved as nullable strings."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Bronze CSV does not exist: {csv_path}")

    return pd.read_csv(csv_path, dtype="string")


def rename_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Rename expected raw columns to Silver snake_case names."""
    missing_columns = [
        raw_column
        for raw_column in RAW_TO_SILVER_COLUMN_MAPPING
        if raw_column not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(f"Bronze CSV is missing expected columns: {missing_columns}")

    return dataframe.rename(columns=RAW_TO_SILVER_COLUMN_MAPPING)


def trim_string_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Trim leading and trailing whitespace from string-like columns."""
    transformed = dataframe.copy()
    string_columns = transformed.select_dtypes(include=["object", "string"]).columns

    for column in string_columns:
        transformed[column] = transformed[column].astype("string").str.strip()

    return transformed


def convert_blank_strings_to_nulls(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Convert empty strings to nullable missing values."""
    return dataframe.replace(r"^\s*$", pd.NA, regex=True)


def _normalize_time_column(time_values: pd.Series) -> pd.Series:
    parsed_time = pd.to_datetime(time_values, format="%I:%M:%S %p", errors="coerce")
    normalized_time = parsed_time.dt.strftime("%H:%M:%S").astype("string")
    return normalized_time.mask(parsed_time.isna(), pd.NA)


def _parse_dates_safely(date_values: pd.Series) -> pd.Series:
    """Parse date values with a day-first fallback for mixed raw CSV strings."""
    parsed_dates = pd.to_datetime(date_values, errors="coerce")
    fallback_dates = pd.to_datetime(date_values, errors="coerce", dayfirst=True)
    return parsed_dates.fillna(fallback_dates)


def _build_admission_timestamp(dataframe: pd.DataFrame) -> pd.Series:
    combined_values = (
        dataframe["patient_admission_date"].astype("string")
        + " "
        + dataframe["patient_admission_time"].astype("string")
    )
    parsed_timestamp = pd.to_datetime(combined_values, errors="coerce")
    return parsed_timestamp


def apply_safe_type_casts(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Apply Silver type normalization without failing the full dataset on bad values.

    Invalid date, timestamp, and numeric values are coerced to null-like values by
    Pandas and are reported later through validation summaries.
    """
    transformed = dataframe.copy()

    transformed["patient_id"] = transformed["patient_id"].astype("string")
    parsed_admission_dates = _parse_dates_safely(transformed["patient_admission_date"])
    transformed["patient_admission_date"] = parsed_admission_dates.dt.date
    transformed["patient_admission_time"] = _normalize_time_column(
        transformed["patient_admission_time"]
    )
    transformed["patient_admission_timestamp"] = _build_admission_timestamp(transformed)

    transformed["patient_age"] = pd.to_numeric(
        transformed["patient_age"], errors="coerce"
    ).astype("Int64")
    transformed["patient_satisfaction_score"] = pd.to_numeric(
        transformed["patient_satisfaction_score"], errors="coerce"
    ).astype("Float64")
    transformed["patient_waittime"] = pd.to_numeric(
        transformed["patient_waittime"], errors="coerce"
    ).astype("Float64")

    technical_loaded_at = pd.Timestamp.now(tz="UTC").isoformat()
    transformed["silver_loaded_at_utc"] = technical_loaded_at

    return transformed


def build_silver_dataframe(bronze_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build the Silver patient flow DataFrame from a loaded Bronze DataFrame."""
    normalized_dataframe = normalize_silver_structure(bronze_dataframe)
    transformed = apply_safe_type_casts(normalized_dataframe)

    return transformed


def normalize_silver_structure(bronze_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Apply rename and string cleanup before type casting."""
    transformed = rename_columns(bronze_dataframe)
    transformed = trim_string_columns(transformed)
    transformed = convert_blank_strings_to_nulls(transformed)
    return transformed


def write_silver_csv(dataframe: pd.DataFrame, output_path: Path | None = None) -> Path:
    """Write the Silver DataFrame to a local CSV artifact."""
    target_path = output_path or get_default_silver_output_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(target_path, index=False)
    return target_path


def write_silver_metadata(
    metadata: dict[str, Any], output_path: Path | None = None
) -> Path:
    """Write a lightweight Silver metadata JSON artifact."""
    target_path = output_path or get_default_silver_metadata_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)
        metadata_file.write("\n")
    return target_path


def build_silver_metadata(
    bronze_csv_path: Path,
    silver_output_path: Path,
    bronze_dataframe: pd.DataFrame,
    silver_dataframe: pd.DataFrame,
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build lightweight metadata for the Silver artifact."""
    return {
        "engine": "pandas",
        "source_path": path_relative_to_project(bronze_csv_path),
        "output_path": path_relative_to_project(silver_output_path),
        "row_count_input": int(len(bronze_dataframe)),
        "row_count_output": int(len(silver_dataframe)),
        "column_count_output": int(len(silver_dataframe.columns)),
        "columns": list(silver_dataframe.columns),
        "rename_mapping": RAW_TO_SILVER_COLUMN_MAPPING,
        "validation_summary": validation_summary,
    }


def run_silver_pipeline(
    bronze_csv_path: Path | None = None,
    silver_output_path: Path | None = None,
    silver_metadata_path: Path | None = None,
) -> dict[str, Any]:
    """Run the Pandas-based Silver v1 pipeline and write local artifacts."""
    source_path = bronze_csv_path or resolve_main_bronze_csv()
    bronze_dataframe = load_bronze_csv(source_path)
    normalized_dataframe = normalize_silver_structure(bronze_dataframe)
    silver_dataframe = apply_safe_type_casts(normalized_dataframe)
    output_path = write_silver_csv(silver_dataframe, silver_output_path)

    from quality.checks import validate_silver_dataframe

    validation_summary = validate_silver_dataframe(
        bronze_dataframe=normalized_dataframe,
        silver_dataframe=silver_dataframe,
        expected_columns=SILVER_COLUMNS,
        required_columns=[
            "patient_id",
            "patient_admission_date",
            "patient_admission_time",
            "patient_admission_timestamp",
            "silver_loaded_at_utc",
        ],
        numeric_columns=NUMERIC_COLUMNS,
    )

    metadata = build_silver_metadata(
        bronze_csv_path=source_path,
        silver_output_path=output_path,
        bronze_dataframe=bronze_dataframe,
        silver_dataframe=silver_dataframe,
        validation_summary=validation_summary,
    )
    metadata_path = write_silver_metadata(metadata, silver_metadata_path)

    return {
        "source_path": path_relative_to_project(source_path),
        "output_path": path_relative_to_project(output_path),
        "metadata_path": path_relative_to_project(metadata_path),
        "input_rows": int(len(bronze_dataframe)),
        "output_rows": int(len(silver_dataframe)),
        "columns": list(silver_dataframe.columns),
        "duplicate_rows": int(silver_dataframe.duplicated().sum()),
        "validation_summary": validation_summary,
    }
