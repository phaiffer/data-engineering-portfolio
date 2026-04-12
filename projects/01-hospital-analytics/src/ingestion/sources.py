from __future__ import annotations

from pathlib import Path

import kagglehub


DATASET_HANDLE = "hassanjameelahmed/healthcare-analytics-patient-flow-data"
DATASET_FOLDER_NAME = "healthcare_analytics_patient_flow"


def get_project_root() -> Path:
    """
    Return the root directory of the hospital analytics project.
    """
    return Path(__file__).resolve().parents[2]


def get_raw_data_dir() -> Path:
    """
    Return the target directory for raw bronze data.
    """
    project_root = get_project_root()
    raw_dir = project_root / "data" / "bronze" / "raw" / DATASET_FOLDER_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir


def download_hospital_dataset() -> Path:
    """
    Download the hospital dataset from Kaggle into the raw bronze directory.
    """
    raw_dir = get_raw_data_dir()

    dataset_path = kagglehub.dataset_download(
        DATASET_HANDLE,
        output_dir=str(raw_dir),
    )

    return Path(dataset_path)

def ingest_raw_sources() -> None:
    """Placeholder for raw ingestion orchestration."""
    raise NotImplementedError("Raw ingestion logic has not been implemented yet.")

if __name__ == "__main__":
    downloaded_path = download_hospital_dataset()
    print(f"Dataset downloaded to: {downloaded_path}")
