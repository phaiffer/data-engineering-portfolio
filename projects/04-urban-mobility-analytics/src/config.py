from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional until project dependencies are installed
    def load_dotenv(*_args: object, **_kwargs: object) -> bool:
        return False


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True, order=True)
class MonthPartition:
    """Represent one calendar month used as a pipeline planning unit."""

    year: int
    month: int

    def __post_init__(self) -> None:
        if self.month < 1 or self.month > 12:
            raise ValueError(f"Month must be between 1 and 12. Received: {self.month}")

    @classmethod
    def from_string(cls, value: str) -> "MonthPartition":
        """Parse a month in YYYY-MM format."""
        if not re.fullmatch(r"\d{4}-\d{2}", value):
            raise ValueError(f"Month must use YYYY-MM format. Received: {value}")

        year, month = value.split("-")
        return cls(year=int(year), month=int(month))

    @property
    def month_id(self) -> str:
        """Return the canonical month identifier used in manifests."""
        return f"{self.year:04d}-{self.month:02d}"

    def to_dict(self) -> dict[str, int | str]:
        """Return a serializable representation."""
        return {"year": self.year, "month": self.month, "month_id": self.month_id}


@dataclass(frozen=True)
class ProjectSettings:
    """Centralize environment-driven project settings."""

    project_name: str
    dataset_family: str
    dataset_slug: str
    source_page_url: str
    source_dictionary_url: str
    source_base_url: str
    default_start_month: str
    default_end_month: str
    request_timeout_seconds: int
    download_chunk_size_bytes: int
    bronze_raw_dir: Path
    bronze_metadata_dir: Path
    bronze_state_dir: Path
    bronze_ingestion_state_path: Path
    bronze_state_path: Path
    silver_tables_dir: Path
    silver_metadata_dir: Path
    silver_state_dir: Path
    silver_state_path: Path
    gold_tables_dir: Path
    gold_metadata_dir: Path
    gold_state_dir: Path
    gold_state_path: Path


def get_project_root() -> Path:
    """Return the project root directory."""
    return PROJECT_ROOT


@lru_cache(maxsize=1)
def get_settings() -> ProjectSettings:
    """Load project settings from environment variables with safe defaults."""
    bronze_raw_dir = PROJECT_ROOT / os.getenv(
        "BRONZE_RAW_DIR",
        "data/bronze/raw",
    )
    bronze_metadata_dir = PROJECT_ROOT / os.getenv(
        "BRONZE_METADATA_DIR",
        "data/bronze/metadata",
    )
    bronze_state_dir = PROJECT_ROOT / os.getenv(
        "BRONZE_STATE_DIR",
        "data/bronze/state",
    )
    silver_tables_dir = PROJECT_ROOT / os.getenv(
        "SILVER_TABLES_DIR",
        "data/silver/tables",
    )
    silver_metadata_dir = PROJECT_ROOT / os.getenv(
        "SILVER_METADATA_DIR",
        "data/silver/metadata",
    )
    silver_state_dir = PROJECT_ROOT / os.getenv(
        "SILVER_STATE_DIR",
        "data/silver/state",
    )
    gold_tables_dir = PROJECT_ROOT / os.getenv(
        "GOLD_TABLES_DIR",
        "data/gold/tables",
    )
    gold_metadata_dir = PROJECT_ROOT / os.getenv(
        "GOLD_METADATA_DIR",
        "data/gold/metadata",
    )
    gold_state_dir = PROJECT_ROOT / os.getenv(
        "GOLD_STATE_DIR",
        "data/gold/state",
    )

    return ProjectSettings(
        project_name=os.getenv("PROJECT_NAME", "urban-mobility-analytics"),
        dataset_family="nyc_tlc_trip_record_data",
        dataset_slug=os.getenv("DATASET_SLUG", "yellow_taxi"),
        source_page_url=os.getenv(
            "SOURCE_PAGE_URL",
            "https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page",
        ),
        source_dictionary_url=os.getenv(
            "SOURCE_DICTIONARY_URL",
            "https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf",
        ),
        source_base_url=os.getenv(
            "SOURCE_BASE_URL",
            "https://d37ci6vzurychx.cloudfront.net/trip-data",
        ),
        default_start_month=os.getenv("DEFAULT_START_MONTH", "2024-01"),
        default_end_month=os.getenv("DEFAULT_END_MONTH", "2024-02"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "120")),
        download_chunk_size_bytes=int(os.getenv("DOWNLOAD_CHUNK_SIZE_BYTES", "1048576")),
        bronze_raw_dir=bronze_raw_dir,
        bronze_metadata_dir=bronze_metadata_dir,
        bronze_state_dir=bronze_state_dir,
        bronze_ingestion_state_path=bronze_state_dir / "ingestion_state.json",
        bronze_state_path=bronze_state_dir / "bronze_state.json",
        silver_tables_dir=silver_tables_dir,
        silver_metadata_dir=silver_metadata_dir,
        silver_state_dir=silver_state_dir,
        silver_state_path=silver_state_dir / "silver_state.json",
        gold_tables_dir=gold_tables_dir,
        gold_metadata_dir=gold_metadata_dir,
        gold_state_dir=gold_state_dir,
        gold_state_path=gold_state_dir / "gold_state.json",
    )


def ensure_runtime_directories() -> None:
    """Create the runtime directory structure if it does not already exist."""
    settings = get_settings()
    for directory in (
        settings.bronze_raw_dir,
        settings.bronze_metadata_dir,
        settings.bronze_state_dir,
        settings.silver_tables_dir,
        settings.silver_metadata_dir,
        settings.silver_state_dir,
        settings.gold_tables_dir,
        settings.gold_metadata_dir,
        settings.gold_state_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)


def iter_month_range(start_month: MonthPartition, end_month: MonthPartition) -> list[MonthPartition]:
    """Return all months between two bounds, inclusive."""
    if start_month > end_month:
        raise ValueError(
            "Start month cannot be later than end month. "
            f"Received: {start_month.month_id} > {end_month.month_id}"
        )

    months: list[MonthPartition] = []
    cursor_year = start_month.year
    cursor_month = start_month.month

    while (cursor_year, cursor_month) <= (end_month.year, end_month.month):
        months.append(MonthPartition(cursor_year, cursor_month))
        if cursor_month == 12:
            cursor_year += 1
            cursor_month = 1
        else:
            cursor_month += 1

    return months


def resolve_month_window(
    *,
    start_month: str | None = None,
    end_month: str | None = None,
) -> list[MonthPartition]:
    """Resolve the configured month window into concrete planning units."""
    settings = get_settings()
    start = MonthPartition.from_string(start_month or settings.default_start_month)
    end = MonthPartition.from_string(end_month or settings.default_end_month)
    return iter_month_range(start, end)


def path_relative_to_project(path: Path) -> str:
    """Return a stable project-relative string path for logs and metadata."""
    return str(path.resolve().relative_to(PROJECT_ROOT.resolve()))


def build_bronze_raw_file_path(month_partition: MonthPartition) -> Path:
    """Return the raw Bronze output path for one landed month."""
    settings = get_settings()
    return (
        settings.bronze_raw_dir
        / settings.dataset_slug
        / f"year={month_partition.year:04d}"
        / f"month={month_partition.month:02d}"
        / "source.parquet"
    )


def build_silver_output_file_path(
    *,
    source_month: MonthPartition,
    partition_year: int,
    partition_month: int,
) -> Path:
    """Return the partitioned Silver output path for one source month."""
    settings = get_settings()
    filename = f"{settings.dataset_slug}_trips_{source_month.month_id}.parquet"
    return (
        settings.silver_tables_dir
        / "trips"
        / f"pickup_year={partition_year:04d}"
        / f"pickup_month={partition_month:02d}"
        / filename
    )


def build_gold_output_file_path(
    *,
    table_name: str,
    source_month: MonthPartition,
    partition_year: int,
    partition_month: int,
) -> Path:
    """Return the partitioned Gold output path for one aggregated table."""
    settings = get_settings()
    filename = f"{table_name}_{source_month.month_id}.parquet"
    return (
        settings.gold_tables_dir
        / table_name
        / f"pickup_year={partition_year:04d}"
        / f"pickup_month={partition_month:02d}"
        / filename
    )
