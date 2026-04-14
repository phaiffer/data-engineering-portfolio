from __future__ import annotations

from pathlib import Path
from typing import Any


DATASET_HANDLE = "uom190346a/ai-powered-job-market-insights"
DATASET_FOLDER_NAME = "ai_powered_job_market_insights"
SUPPORTED_DATA_EXTENSIONS = frozenset({".csv"})


def get_project_root() -> Path:
    """Return the root directory of the job market analytics project."""
    return Path(__file__).resolve().parents[2]


def get_raw_data_dir() -> Path:
    """Return the local raw Bronze directory for the Kaggle job market dataset."""
    return get_project_root() / "data" / "bronze" / "raw" / DATASET_FOLDER_NAME


def get_bronze_metadata_dir() -> Path:
    """Return the directory used for Bronze metadata artifacts."""
    return get_project_root() / "data" / "bronze" / "metadata"


def is_supported_data_file(path: Path) -> bool:
    """Return whether a file has a supported raw data extension."""
    return path.is_file() and path.suffix.lower() in SUPPORTED_DATA_EXTENSIONS


def is_real_data_file(path: Path) -> bool:
    """
    Return whether a file should be treated as source data for Bronze profiling.

    KaggleHub can create hidden operational artifacts. Bronze inventories them
    but excludes hidden paths from dataset profiling.
    """
    try:
        relative_parts = path.resolve().relative_to(get_project_root()).parts
    except ValueError:
        relative_parts = path.parts

    return is_supported_data_file(path) and not any(part.startswith(".") for part in relative_parts)


def list_raw_files(raw_data_dir: Path | None = None) -> list[Path]:
    """Recursively list all files found in the raw dataset directory."""
    raw_dir = raw_data_dir or get_raw_data_dir()
    if not raw_dir.exists():
        return []

    return sorted(path for path in raw_dir.rglob("*") if path.is_file())


def list_supported_data_files(raw_data_dir: Path | None = None) -> list[Path]:
    """List supported source data files that can be profiled by Bronze."""
    return [path for path in list_raw_files(raw_data_dir) if is_real_data_file(path)]


def path_relative_to_project(path: Path) -> str:
    """Return a stable project-relative path string when possible."""
    project_root = get_project_root()
    try:
        return path.resolve().relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def describe_raw_file(path: Path) -> dict[str, Any]:
    """Return serializable metadata for one raw file."""
    return {
        "path": path_relative_to_project(path),
        "name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "is_supported_data_file": is_supported_data_file(path),
        "is_selected_for_bronze_profiling": is_real_data_file(path),
    }


def discover_raw_files(raw_data_dir: Path | None = None) -> dict[str, Any]:
    """Return a structured inventory of the raw dataset landing directory."""
    raw_dir = raw_data_dir or get_raw_data_dir()
    raw_files = list_raw_files(raw_dir)
    supported_files = [path for path in raw_files if is_real_data_file(path)]

    return {
        "raw_directory": path_relative_to_project(raw_dir),
        "supported_extensions": sorted(SUPPORTED_DATA_EXTENSIONS),
        "file_count": len(raw_files),
        "supported_data_file_count": len(supported_files),
        "files": [describe_raw_file(path) for path in raw_files],
        "supported_data_files": [path_relative_to_project(path) for path in supported_files],
    }
