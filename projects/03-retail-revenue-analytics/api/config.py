from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class ApiConfig:
    """Runtime configuration for the local retail revenue analytics API."""

    service_name: str
    host: str
    port: int
    debug: bool
    duckdb_path: Path
    marts_schema: str
    cors_allowed_origins: tuple[str, ...]


def load_config() -> ApiConfig:
    """Load API settings from environment variables and project-local .env."""
    load_dotenv(ENV_PATH)

    duckdb_path = Path(
        os.getenv(
            "RETAIL_REVENUE_DUCKDB_PATH",
            PROJECT_ROOT / "data" / "retail_revenue_analytics.duckdb",
        )
    )
    if not duckdb_path.is_absolute():
        duckdb_path = PROJECT_ROOT / duckdb_path

    return ApiConfig(
        service_name=os.getenv(
            "RETAIL_REVENUE_API_SERVICE_NAME",
            "retail-revenue-analytics-api",
        ),
        host=os.getenv("RETAIL_REVENUE_API_HOST", "127.0.0.1"),
        port=int(os.getenv("RETAIL_REVENUE_API_PORT", "5002")),
        debug=os.getenv("RETAIL_REVENUE_API_DEBUG", "false").lower() == "true",
        duckdb_path=duckdb_path,
        marts_schema=os.getenv("RETAIL_REVENUE_DBT_SCHEMA", "marts"),
        cors_allowed_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "RETAIL_REVENUE_API_CORS_ALLOWED_ORIGINS",
                "http://127.0.0.1:5173,http://localhost:5173",
            ).split(",")
            if origin.strip()
        ),
    )
