from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import get_project_root, path_relative_to_project
from quality.checks import validate_silver_dataframe


BRONZE_METADATA_PATH = (
    get_project_root()
    / "data"
    / "bronze"
    / "metadata"
    / "ai_powered_job_market_insights_bronze_metadata.json"
)
SILVER_OUTPUT_DIR = get_project_root() / "data" / "silver"
SILVER_DATASET_FILENAME = "ai_job_market_insights_silver.csv"
SILVER_METADATA_FILENAME = "ai_job_market_insights_silver_metadata.json"

RENAME_MAP = {
    "Job_Title": "job_title",
    "Industry": "industry",
    "Company_Size": "company_size",
    "Location": "location",
    "AI_Adoption_Level": "ai_adoption_level",
    "Automation_Risk": "automation_risk",
    "Required_Skills": "required_skills",
    "Salary_USD": "salary_usd",
    "Remote_Friendly": "remote_friendly",
    "Job_Growth_Projection": "job_growth_projection",
}

EXPECTED_SILVER_COLUMNS = list(RENAME_MAP.values())
CATEGORICAL_COLUMNS = [
    "job_title",
    "industry",
    "company_size",
    "location",
    "ai_adoption_level",
    "automation_risk",
    "required_skills",
    "remote_friendly",
    "job_growth_projection",
]


def load_bronze_metadata(metadata_path: Path | None = None) -> dict[str, Any]:
    """Load the Bronze metadata document that points to the selected raw CSV."""
    path = metadata_path or BRONZE_METADATA_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Bronze metadata was not found at {path}. Run run_bronze.py before run_silver.py."
        )

    return json.loads(path.read_text(encoding="utf-8"))


def get_bronze_selected_csv_path(metadata: dict[str, Any]) -> Path:
    """Resolve the Bronze-selected main CSV path from metadata."""
    selected_main_file = metadata.get("selected_main_file")
    if not selected_main_file:
        raise KeyError("Bronze metadata does not include selected_main_file.")

    selected_path = Path(selected_main_file)
    if selected_path.is_absolute():
        return selected_path

    return get_project_root() / selected_path


def load_bronze_selected_csv(metadata: dict[str, Any]) -> pd.DataFrame:
    """Load the raw CSV selected by the Bronze layer."""
    csv_path = get_bronze_selected_csv_path(metadata)
    if not csv_path.exists():
        raise FileNotFoundError(f"Bronze-selected CSV does not exist: {csv_path}")

    return pd.read_csv(csv_path)


def normalize_categorical_value(value: object) -> object:
    """Normalize compact categorical labels into lowercase analytical tokens."""
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text:
        return pd.NA

    normalized = re.sub(r"[^0-9A-Za-z]+", "_", text)
    normalized = re.sub(r"_+", "_", normalized).strip("_").lower()
    return normalized or pd.NA


def clean_string_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace and convert blank strings to nulls for object-like columns."""
    cleaned = dataframe.copy()
    string_columns = cleaned.select_dtypes(include=["object", "string"]).columns

    for column in string_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
        cleaned[column] = cleaned[column].replace("", pd.NA)

    return cleaned


def transform_silver(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Transform raw Bronze records into the Silver v1 row-level contract."""
    missing_columns = [column for column in RENAME_MAP if column not in dataframe.columns]
    if missing_columns:
        raise ValueError(f"Source data is missing expected Bronze columns: {missing_columns}")

    silver = dataframe.copy()
    silver = silver.rename(columns=RENAME_MAP)
    silver = silver[EXPECTED_SILVER_COLUMNS]
    silver = clean_string_columns(silver)

    for column in CATEGORICAL_COLUMNS:
        silver[column] = silver[column].map(normalize_categorical_value).astype("string")

    silver["salary_usd"] = pd.to_numeric(silver["salary_usd"], errors="coerce")

    return silver


def write_silver_artifacts(
    silver_dataframe: pd.DataFrame,
    validation_summary: dict[str, Any],
    metadata: dict[str, Any],
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Write the Silver dataset and metadata artifacts."""
    target_dir = output_dir or SILVER_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = target_dir / SILVER_DATASET_FILENAME
    metadata_path = target_dir / SILVER_METADATA_FILENAME

    silver_dataframe.to_csv(dataset_path, index=False)

    silver_metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_bronze_metadata": path_relative_to_project(BRONZE_METADATA_PATH),
        "source_bronze_file": metadata["selected_main_file"],
        "silver_dataset": path_relative_to_project(dataset_path),
        "grain_assumption": "one source job-market insight record per raw row",
        "row_count": int(len(silver_dataframe)),
        "column_count": int(len(silver_dataframe.columns)),
        "columns": list(silver_dataframe.columns),
        "rename_map": RENAME_MAP,
        "categorical_columns_normalized": CATEGORICAL_COLUMNS,
        "numeric_columns": ["salary_usd"],
        "validation_summary": validation_summary,
        "silver_scope_notes": [
            "Silver v1 is row-preserving.",
            "No rows are dropped, aggregated, or deduplicated.",
            "Categorical values are normalized into lowercase analytical tokens.",
            "salary_usd is safely converted with pandas.to_numeric(errors='coerce').",
            "Gold marts and production DBT models are future work.",
        ],
    }
    metadata_path.write_text(json.dumps(silver_metadata, indent=2), encoding="utf-8")

    return {"dataset_path": dataset_path, "metadata_path": metadata_path}


def run_silver_pipeline(output_dir: Path | None = None) -> dict[str, Any]:
    """Run the Silver v1 transformation, validation, and artifact write."""
    bronze_metadata = load_bronze_metadata()
    raw_dataframe = load_bronze_selected_csv(bronze_metadata)
    silver_dataframe = transform_silver(raw_dataframe)
    validation_summary = validate_silver_dataframe(
        raw_dataframe=raw_dataframe,
        silver_dataframe=silver_dataframe,
        expected_columns=EXPECTED_SILVER_COLUMNS,
    )
    artifact_paths = write_silver_artifacts(
        silver_dataframe=silver_dataframe,
        validation_summary=validation_summary,
        metadata=bronze_metadata,
        output_dir=output_dir,
    )

    return {
        "source_file": bronze_metadata["selected_main_file"],
        "dataset_path": path_relative_to_project(artifact_paths["dataset_path"]),
        "metadata_path": path_relative_to_project(artifact_paths["metadata_path"]),
        "validation_summary": validation_summary,
    }
