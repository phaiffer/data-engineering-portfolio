from __future__ import annotations

from pathlib import Path

import kagglehub

from ingestion.raw_inventory import DATASET_HANDLE, get_raw_data_dir


def download_job_market_dataset() -> Path:
    """Download the Kaggle job market dataset into the raw Bronze directory."""
    raw_dir = get_raw_data_dir()
    raw_dir.mkdir(parents=True, exist_ok=True)

    dataset_path = kagglehub.dataset_download(
        DATASET_HANDLE,
        output_dir=str(raw_dir),
    )

    return Path(dataset_path)


if __name__ == "__main__":
    downloaded_path = download_job_market_dataset()
    print(f"Dataset downloaded to: {downloaded_path}")
