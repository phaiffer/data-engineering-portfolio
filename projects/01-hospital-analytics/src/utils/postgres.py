from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
import psycopg


def load_project_env() -> None:
    """
    Load environment variables from the project .env file.
    """
    project_root = Path(__file__).resolve().parents[2]
    env_path = project_root / ".env"

    load_dotenv(env_path)


def get_postgres_connection():
    """
    Create and return a PostgreSQL connection using environment variables.
    """
    load_project_env()

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def test_connection() -> None:
    """
    Open a connection, run a simple query, and print the result.
    """
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user;")
            result = cur.fetchone()
            print("Connection successful:", result)


if __name__ == "__main__":
    test_connection()