from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import get_project_root, path_relative_to_project
from processing.silver.pipeline import get_default_silver_output_path


DAILY_PATIENT_FLOW_FILENAME = "daily_patient_flow.csv"
DEPARTMENT_REFERRAL_SUMMARY_FILENAME = "department_referral_summary.csv"
DEMOGRAPHIC_SUMMARY_FILENAME = "demographic_summary.csv"
GOLD_METADATA_FILENAME = "gold_metadata.json"

DAILY_PATIENT_FLOW_COLUMNS = [
    "admission_date",
    "total_patient_events",
    "average_patient_waittime",
    "average_patient_satisfaction_score",
    "admitted_patient_events",
    "null_department_referral_events",
    "null_satisfaction_score_events",
]
DEPARTMENT_REFERRAL_SUMMARY_COLUMNS = [
    "department_referral",
    "total_patient_events",
    "average_patient_waittime",
    "average_patient_satisfaction_score",
    "share_of_total_events",
]
DEMOGRAPHIC_SUMMARY_COLUMNS = [
    "patient_gender",
    "patient_race",
    "patient_age_band",
    "total_patient_events",
    "average_patient_waittime",
    "average_patient_satisfaction_score",
]
REQUIRED_SILVER_COLUMNS = [
    "patient_admission_date",
    "patient_gender",
    "patient_race",
    "patient_age",
    "department_referral",
    "patient_admission_flag",
    "patient_satisfaction_score",
    "patient_waittime",
]
AGE_BAND_LABELS = ["0_17", "18_35", "36_50", "51_65", "66_plus"]


def get_gold_data_dir() -> Path:
    """Return the local Gold output directory for the project."""
    return get_project_root() / "data" / "gold"


def get_default_gold_output_paths() -> dict[str, Path]:
    """Return the default local Gold CSV artifact paths."""
    gold_dir = get_gold_data_dir()
    return {
        "daily_patient_flow": gold_dir / DAILY_PATIENT_FLOW_FILENAME,
        "department_referral_summary": gold_dir
        / DEPARTMENT_REFERRAL_SUMMARY_FILENAME,
        "demographic_summary": gold_dir / DEMOGRAPHIC_SUMMARY_FILENAME,
    }


def get_default_gold_metadata_path() -> Path:
    """Return the default local Gold metadata artifact path."""
    return get_gold_data_dir() / GOLD_METADATA_FILENAME


def load_silver_dataset(silver_path: Path | None = None) -> pd.DataFrame:
    """Load the Silver patient flow dataset used as the Gold v1 source."""
    source_path = silver_path or get_default_silver_output_path()
    if not source_path.exists():
        raise FileNotFoundError(f"Silver dataset does not exist: {source_path}")

    return pd.read_csv(source_path)


def validate_silver_source(dataframe: pd.DataFrame) -> dict[str, Any]:
    """Validate the minimal Silver columns required by the Gold v1 aggregates."""
    missing_columns = [
        column for column in REQUIRED_SILVER_COLUMNS if column not in dataframe.columns
    ]
    return {
        "passed": not missing_columns and len(dataframe) > 0,
        "missing_columns": missing_columns,
        "source_row_count": int(len(dataframe)),
        "source_is_empty": bool(dataframe.empty),
    }


def prepare_gold_source(silver_dataframe: pd.DataFrame) -> pd.DataFrame:
    """Prepare a typed working copy of Silver for Gold aggregations."""
    transformed = silver_dataframe.copy()
    source_validation = validate_silver_source(transformed)
    if not source_validation["passed"]:
        raise ValueError(f"Silver source is not valid for Gold: {source_validation}")

    transformed["patient_admission_date"] = pd.to_datetime(
        transformed["patient_admission_date"], errors="coerce"
    )
    transformed["patient_age"] = pd.to_numeric(
        transformed["patient_age"], errors="coerce"
    )
    transformed["patient_satisfaction_score"] = pd.to_numeric(
        transformed["patient_satisfaction_score"], errors="coerce"
    )
    transformed["patient_waittime"] = pd.to_numeric(
        transformed["patient_waittime"], errors="coerce"
    )
    transformed["is_admitted_patient_event"] = (
        transformed["patient_admission_flag"].astype("string").str.strip()
        == "Admission"
    ).astype("int64")

    return transformed


def build_daily_patient_flow(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build one Gold row per admission date from the Silver patient flow data."""
    working = dataframe.copy()
    working["admission_date"] = working["patient_admission_date"].dt.date
    working["null_department_referral_event"] = working[
        "department_referral"
    ].isna()
    working["null_satisfaction_score_event"] = working[
        "patient_satisfaction_score"
    ].isna()

    grouped = (
        working.groupby("admission_date", dropna=False)
        .agg(
            total_patient_events=("patient_admission_date", "size"),
            average_patient_waittime=("patient_waittime", "mean"),
            average_patient_satisfaction_score=(
                "patient_satisfaction_score",
                "mean",
            ),
            admitted_patient_events=("is_admitted_patient_event", "sum"),
            null_department_referral_events=(
                "null_department_referral_event",
                "sum",
            ),
            null_satisfaction_score_events=(
                "null_satisfaction_score_event",
                "sum",
            ),
        )
        .reset_index()
    )

    return grouped[DAILY_PATIENT_FLOW_COLUMNS].sort_values("admission_date")


def build_department_referral_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build one Gold row per department referral value, preserving null referrals."""
    grouped = (
        dataframe.groupby("department_referral", dropna=False)
        .agg(
            total_patient_events=("department_referral", "size"),
            average_patient_waittime=("patient_waittime", "mean"),
            average_patient_satisfaction_score=(
                "patient_satisfaction_score",
                "mean",
            ),
        )
        .reset_index()
    )

    source_rows = len(dataframe)
    grouped["share_of_total_events"] = grouped["total_patient_events"] / source_rows

    return grouped[DEPARTMENT_REFERRAL_SUMMARY_COLUMNS].sort_values(
        ["total_patient_events", "department_referral"],
        ascending=[False, True],
        na_position="first",
    )


def add_patient_age_band(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Add a simple patient age band for Gold demographic analysis."""
    transformed = dataframe.copy()
    transformed["patient_age_band"] = pd.cut(
        transformed["patient_age"],
        bins=[-1, 17, 35, 50, 65, float("inf")],
        labels=AGE_BAND_LABELS,
    ).astype("string")
    return transformed


def build_demographic_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build one Gold row per gender, race, and age-band grouping."""
    working = add_patient_age_band(dataframe)
    grouped = (
        working.groupby(
            ["patient_gender", "patient_race", "patient_age_band"], dropna=False
        )
        .agg(
            total_patient_events=("patient_gender", "size"),
            average_patient_waittime=("patient_waittime", "mean"),
            average_patient_satisfaction_score=(
                "patient_satisfaction_score",
                "mean",
            ),
        )
        .reset_index()
    )

    return grouped[DEMOGRAPHIC_SUMMARY_COLUMNS].sort_values(
        ["patient_gender", "patient_race", "patient_age_band"], na_position="last"
    )


def build_gold_outputs(silver_dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build all Gold v1 analytical outputs from the Silver DataFrame."""
    source = prepare_gold_source(silver_dataframe)
    return {
        "daily_patient_flow": build_daily_patient_flow(source),
        "department_referral_summary": build_department_referral_summary(source),
        "demographic_summary": build_demographic_summary(source),
    }


def validate_gold_output(
    dataframe: pd.DataFrame, expected_columns: list[str]
) -> dict[str, Any]:
    """Run lightweight checks for one Gold output DataFrame."""
    actual_columns = list(dataframe.columns)
    missing_columns = [
        column for column in expected_columns if column not in actual_columns
    ]
    unexpected_columns = [
        column for column in actual_columns if column not in expected_columns
    ]
    total_events_is_valid = True
    if "total_patient_events" in dataframe.columns:
        total_events_is_valid = bool((dataframe["total_patient_events"] > 0).all())

    return {
        "passed": (
            not dataframe.empty
            and not missing_columns
            and not unexpected_columns
            and total_events_is_valid
        ),
        "row_count": int(len(dataframe)),
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "total_events_is_valid": total_events_is_valid,
    }


def validate_gold_outputs(outputs: dict[str, pd.DataFrame]) -> dict[str, Any]:
    """Run lightweight validation checks across the Gold v1 outputs."""
    checks = {
        "daily_patient_flow": validate_gold_output(
            outputs["daily_patient_flow"], DAILY_PATIENT_FLOW_COLUMNS
        ),
        "department_referral_summary": validate_gold_output(
            outputs["department_referral_summary"],
            DEPARTMENT_REFERRAL_SUMMARY_COLUMNS,
        ),
        "demographic_summary": validate_gold_output(
            outputs["demographic_summary"], DEMOGRAPHIC_SUMMARY_COLUMNS
        ),
    }
    department_share_total = float(
        outputs["department_referral_summary"]["share_of_total_events"].sum()
    )
    checks["department_referral_share_total"] = {
        "passed": abs(department_share_total - 1.0) < 0.000001,
        "value": department_share_total,
    }

    return {
        "passed": all(check["passed"] for check in checks.values()),
        "checks": checks,
    }


def write_gold_outputs(
    outputs: dict[str, pd.DataFrame], output_paths: dict[str, Path] | None = None
) -> dict[str, Path]:
    """Write Gold output DataFrames to local CSV artifacts."""
    paths = output_paths or get_default_gold_output_paths()
    for name, dataframe in outputs.items():
        target_path = paths[name]
        target_path.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_csv(target_path, index=False)

    return paths


def build_gold_metadata(
    silver_path: Path,
    output_paths: dict[str, Path],
    outputs: dict[str, pd.DataFrame],
    validation_summary: dict[str, Any],
) -> dict[str, Any]:
    """Build lightweight metadata for the Gold v1 artifacts."""
    return {
        "engine": "pandas",
        "source_path": path_relative_to_project(silver_path),
        "outputs": {
            name: {
                "path": path_relative_to_project(path),
                "row_count": int(len(outputs[name])),
                "columns": list(outputs[name].columns),
            }
            for name, path in output_paths.items()
        },
        "null_handling": {
            "averages": "Pandas mean ignores null numeric values by default.",
            "department_referral": (
                "Null department_referral values are preserved in the grouped "
                "output with groupby(dropna=False) and appear as blank/null in CSV."
            ),
        },
        "admission_flag_rule": (
            "admitted_patient_events counts records where patient_admission_flag "
            "equals the exact Silver value 'Admission'. No additional business "
            "semantics are inferred."
        ),
        "validation_summary": validation_summary,
    }


def write_gold_metadata(
    metadata: dict[str, Any], output_path: Path | None = None
) -> Path:
    """Write a lightweight Gold metadata JSON artifact."""
    target_path = output_path or get_default_gold_metadata_path()
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with target_path.open("w", encoding="utf-8") as metadata_file:
        json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)
        metadata_file.write("\n")
    return target_path


def run_gold_pipeline(
    silver_path: Path | None = None,
    output_paths: dict[str, Path] | None = None,
    metadata_path: Path | None = None,
) -> dict[str, Any]:
    """Run the Pandas-based Gold v1 pipeline and write local artifacts."""
    source_path = silver_path or get_default_silver_output_path()
    silver_dataframe = load_silver_dataset(source_path)
    source_validation = validate_silver_source(silver_dataframe)
    outputs = build_gold_outputs(silver_dataframe)
    written_paths = write_gold_outputs(outputs, output_paths)
    validation_summary = validate_gold_outputs(outputs)
    metadata = build_gold_metadata(
        silver_path=source_path,
        output_paths=written_paths,
        outputs=outputs,
        validation_summary=validation_summary,
    )
    written_metadata_path = write_gold_metadata(metadata, metadata_path)

    return {
        "source_path": path_relative_to_project(source_path),
        "source_validation": source_validation,
        "metadata_path": path_relative_to_project(written_metadata_path),
        "outputs": {
            name: {
                "path": path_relative_to_project(path),
                "row_count": int(len(outputs[name])),
                "columns": list(outputs[name].columns),
            }
            for name, path in written_paths.items()
        },
        "validation_summary": validation_summary,
    }
