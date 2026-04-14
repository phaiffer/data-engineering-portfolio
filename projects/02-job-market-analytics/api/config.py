from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class ApiConfig:
    """Runtime configuration for the local job-market dashboard API."""

    service_name: str
    host: str
    port: int
    debug: bool
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str
    silver_schema: str
    silver_table: str
    marts_schema: str
    cors_allowed_origins: tuple[str, ...]


def load_config() -> ApiConfig:
    """Load API and PostgreSQL settings from the project-local .env file."""
    load_dotenv(ENV_PATH)

    return ApiConfig(
        service_name=os.getenv("JOB_MARKET_API_SERVICE_NAME", "job-market-analytics-api"),
        host=os.getenv("JOB_MARKET_API_HOST", "127.0.0.1"),
        port=int(os.getenv("JOB_MARKET_API_PORT", "5001")),
        debug=os.getenv("JOB_MARKET_API_DEBUG", "false").lower() == "true",
        postgres_host=os.getenv(
            "JOB_MARKET_POSTGRES_HOST",
            os.getenv("POSTGRES_HOST", "localhost"),
        ),
        postgres_port=int(
            os.getenv("JOB_MARKET_POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432"))
        ),
        postgres_db=os.getenv(
            "JOB_MARKET_POSTGRES_DB",
            os.getenv("POSTGRES_DB", "job_market_analytics"),
        ),
        postgres_user=os.getenv(
            "JOB_MARKET_POSTGRES_USER",
            os.getenv("POSTGRES_USER", "postgres"),
        ),
        postgres_password=os.getenv(
            "JOB_MARKET_POSTGRES_PASSWORD",
            os.getenv("POSTGRES_PASSWORD", "postgres"),
        ),
        silver_schema=os.getenv(
            "POSTGRES_ANALYTICS_SCHEMA",
            os.getenv("JOB_MARKET_SILVER_SCHEMA", "analytics"),
        ),
        silver_table=os.getenv(
            "POSTGRES_SILVER_TABLE",
            os.getenv("JOB_MARKET_SILVER_TABLE", "job_market_insights_silver"),
        ),
        marts_schema=os.getenv(
            "POSTGRES_MARTS_SCHEMA",
            os.getenv("JOB_MARKET_DBT_SCHEMA", "marts"),
        ),
        cors_allowed_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "JOB_MARKET_API_CORS_ALLOWED_ORIGINS",
                "http://127.0.0.1:5173,http://localhost:5173",
            ).split(",")
            if origin.strip()
        ),
    )
