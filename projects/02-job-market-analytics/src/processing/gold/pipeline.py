from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ingestion.raw_inventory import get_project_root, path_relative_to_project
from quality.checks import validate_gold_outputs


SILVER_DATASET_PATH = get_project_root() / "data" / "silver" / "ai_job_market_insights_silver.csv"
GOLD_OUTPUT_DIR = get_project_root() / "data" / "gold"

SUMMARY_METRIC_COLUMNS = [
    "total_records",
    "average_salary_usd",
    "median_salary_usd",
    "min_salary_usd",
    "max_salary_usd",
    "remote_friendly_share",
    "high_automation_risk_share",
    "high_ai_adoption_share",
    "growth_projection_share",
]

EXPECTED_GOLD_COLUMNS = {
    "job_title_summary": ["job_title", *SUMMARY_METRIC_COLUMNS],
    "industry_summary": ["industry", *SUMMARY_METRIC_COLUMNS],
    "location_summary": ["location", *SUMMARY_METRIC_COLUMNS],
    "automation_ai_summary": [
        "automation_risk",
        "ai_adoption_level",
        "total_records",
        "average_salary_usd",
        "median_salary_usd",
        "remote_friendly_share",
        "growth_projection_share",
    ],
}

GOLD_FILENAMES = {
    "job_title_summary": "job_title_summary.csv",
    "industry_summary": "industry_summary.csv",
    "location_summary": "location_summary.csv",
    "automation_ai_summary": "automation_ai_summary.csv",
}


def load_silver_dataset(silver_path: Path | None = None) -> pd.DataFrame:
    """Load the Silver dataset used as the only Gold source."""
    path = silver_path or SILVER_DATASET_PATH
    if not path.exists():
        raise FileNotFoundError(f"Silver dataset was not found at {path}. Run run_silver.py first.")

    return pd.read_csv(path)


def _share_equals(series: pd.Series, expected_value: str) -> Any:
    """Return the share of records equal to the expected normalized category."""
    if len(series) == 0:
        return pd.NA

    return float((series == expected_value).mean())


def build_dimension_summary(dataframe: pd.DataFrame, group_column: str) -> pd.DataFrame:
    """Build a reusable one-dimension Gold summary."""
    summary = (
        dataframe.groupby(group_column, dropna=False)
        .agg(
            total_records=("salary_usd", "size"),
            average_salary_usd=("salary_usd", "mean"),
            median_salary_usd=("salary_usd", "median"),
            min_salary_usd=("salary_usd", "min"),
            max_salary_usd=("salary_usd", "max"),
            remote_friendly_share=("remote_friendly", lambda series: _share_equals(series, "yes")),
            high_automation_risk_share=("automation_risk", lambda series: _share_equals(series, "high")),
            high_ai_adoption_share=("ai_adoption_level", lambda series: _share_equals(series, "high")),
            growth_projection_share=("job_growth_projection", lambda series: _share_equals(series, "growth")),
        )
        .reset_index()
        .sort_values(["total_records", group_column], ascending=[False, True])
        .reset_index(drop=True)
    )

    return summary


def build_automation_ai_summary(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build a Gold summary by automation risk and AI adoption level."""
    summary = (
        dataframe.groupby(["automation_risk", "ai_adoption_level"], dropna=False)
        .agg(
            total_records=("salary_usd", "size"),
            average_salary_usd=("salary_usd", "mean"),
            median_salary_usd=("salary_usd", "median"),
            remote_friendly_share=("remote_friendly", lambda series: _share_equals(series, "yes")),
            growth_projection_share=("job_growth_projection", lambda series: _share_equals(series, "growth")),
        )
        .reset_index()
        .sort_values(["automation_risk", "ai_adoption_level"])
        .reset_index(drop=True)
    )

    return summary


def build_gold_outputs(silver_dataframe: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Build all Gold v1 analytical outputs from the Silver dataset."""
    return {
        "job_title_summary": build_dimension_summary(silver_dataframe, "job_title"),
        "industry_summary": build_dimension_summary(silver_dataframe, "industry"),
        "location_summary": build_dimension_summary(silver_dataframe, "location"),
        "automation_ai_summary": build_automation_ai_summary(silver_dataframe),
    }


def write_gold_artifacts(
    outputs: dict[str, pd.DataFrame],
    validation_summary: dict[str, Any],
    output_dir: Path | None = None,
) -> dict[str, Path]:
    """Write Gold output CSVs and metadata."""
    target_dir = output_dir or GOLD_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    artifact_paths: dict[str, Path] = {}
    for name, dataframe in outputs.items():
        output_path = target_dir / GOLD_FILENAMES[name]
        dataframe.to_csv(output_path, index=False)
        artifact_paths[name] = output_path

    metadata_path = target_dir / "gold_metadata.json"
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_silver_dataset": path_relative_to_project(SILVER_DATASET_PATH),
        "gold_outputs": {
            name: {
                "path": path_relative_to_project(path),
                "row_count": int(len(outputs[name])),
                "columns": list(outputs[name].columns),
            }
            for name, path in artifact_paths.items()
        },
        "metric_assumptions": [
            "Salary metrics use numeric salary_usd and ignore nulls by Pandas aggregation behavior.",
            "remote_friendly_share is the share of records where remote_friendly = 'yes'.",
            "high_automation_risk_share is the share of records where automation_risk = 'high'.",
            "high_ai_adoption_share is the share of records where ai_adoption_level = 'high'.",
            "growth_projection_share is the share of records where job_growth_projection = 'growth'.",
            "No numeric score is assigned to job_growth_projection because the source field is categorical.",
        ],
        "validation_summary": validation_summary,
        "gold_scope_notes": [
            "Gold v1 is implemented as local Pandas summaries.",
            "Gold v1 does not create serving tables, an API, a dashboard, or production DBT marts.",
            "All Gold outputs read only from the Silver artifact.",
        ],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    artifact_paths["metadata"] = metadata_path

    return artifact_paths


def run_gold_pipeline(output_dir: Path | None = None) -> dict[str, Any]:
    """Run the Gold v1 transformation, validation, and artifact write."""
    silver_dataframe = load_silver_dataset()
    outputs = build_gold_outputs(silver_dataframe)
    validation_summary = validate_gold_outputs(
        outputs=outputs,
        expected_columns=EXPECTED_GOLD_COLUMNS,
    )
    artifact_paths = write_gold_artifacts(
        outputs=outputs,
        validation_summary=validation_summary,
        output_dir=output_dir,
    )

    return {
        "source_silver_dataset": path_relative_to_project(SILVER_DATASET_PATH),
        "artifact_paths": {
            name: path_relative_to_project(path) for name, path in artifact_paths.items()
        },
        "output_row_counts": {name: int(len(dataframe)) for name, dataframe in outputs.items()},
        "validation_summary": validation_summary,
    }
