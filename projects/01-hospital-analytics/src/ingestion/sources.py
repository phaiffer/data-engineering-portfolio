from __future__ import annotations

from pathlib import Path

import kagglehub

from ingestion.raw_inventory import DATASET_HANDLE, get_raw_data_dir


def download_hospital_dataset() -> Path:
    """
    Download the hospital dataset from Kaggle into the raw bronze directory.
    """
    raw_dir = get_raw_data_dir()
    raw_dir.mkdir(parents=True, exist_ok=True)

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
