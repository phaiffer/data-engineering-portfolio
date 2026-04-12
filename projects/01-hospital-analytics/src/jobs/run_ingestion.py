from __future__ import annotations
from ingestion.sources import download_hospital_dataset

def main() -> None:
    downloaded_path = download_hospital_dataset()
    print(f"Ingestion completed. Dataset available at: {downloaded_path}")
    
if __name__ == "__main__":
    main()
