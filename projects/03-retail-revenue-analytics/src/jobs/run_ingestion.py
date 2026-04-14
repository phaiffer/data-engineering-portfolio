from __future__ import annotations

import sys
from pathlib import Path


PROJECT_SRC = Path(__file__).resolve().parents[1]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from ingestion.sources import download_retail_revenue_dataset  # noqa: E402


def main() -> None:
    """Download the Olist Kaggle dataset into the raw Bronze area."""
    downloaded_path = download_retail_revenue_dataset()
    print(f"Ingestion completed. Dataset available at: {downloaded_path}")


if __name__ == "__main__":
    main()
