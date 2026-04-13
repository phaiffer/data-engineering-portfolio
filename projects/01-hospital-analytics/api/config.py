from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class ApiConfig:
    """Runtime configuration for the local Flask API."""

    service_name: str
    host: str
    port: int
    debug: bool
    postgres_host: str | None
    postgres_port: str | None
    postgres_db: str | None
    postgres_user: str | None
    postgres_password: str | None
    serving_schema: str


def load_config() -> ApiConfig:
    """Load API and PostgreSQL settings from the project .env file."""
    load_dotenv(ENV_PATH)

    return ApiConfig(
        service_name=os.getenv("API_SERVICE_NAME", "hospital-analytics-api"),
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "5000")),
        debug=os.getenv("API_DEBUG", "false").lower() == "true",
        postgres_host=os.getenv("POSTGRES_HOST"),
        postgres_port=os.getenv("POSTGRES_PORT"),
        postgres_db=os.getenv("POSTGRES_DB"),
        postgres_user=os.getenv("POSTGRES_USER"),
        postgres_password=os.getenv("POSTGRES_PASSWORD"),
        serving_schema=os.getenv("POSTGRES_SCHEMA_SERVING", "serving"),
    )
