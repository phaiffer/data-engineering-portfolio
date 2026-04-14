# Job Market Analytics DBT

This directory contains the first real DBT layer for the job market analytics project.

The DBT implementation is intentionally local and portfolio-oriented. It uses DuckDB through `dbt-duckdb` and reads the standardized Silver CSV produced by the existing Python pipeline. It does not read raw Bronze data directly, create serving tables in PostgreSQL, or replace the Python Gold v1 artifacts yet.

## Source Strategy

DBT reads:

```text
../data/silver/ai_job_market_insights_silver.csv
```

as the source `local_silver.ai_job_market_insights_silver`.

This keeps DBT focused on SQL modeling over the already standardized Silver contract:

- Silver v1 remains the row-preserving Python output.
- DBT staging keeps the same row grain and casts fields for SQL modeling.
- DBT intermediate models add only source-supported reusable flags.
- DBT marts formalize the same analytical grains used by Python Gold v1.

The local DuckDB database is written to:

```text
../data/job_market_analytics.duckdb
```

The Silver path can be overridden at runtime:

```powershell
dbt run --profiles-dir . --vars "{silver_dataset_path: '../data/silver/ai_job_market_insights_silver.csv'}"
```

## Model Layers

- `models/staging/`: source-aligned DBT staging over the Silver artifact.
- `models/intermediate/`: row-level enrichment flags such as `is_remote_friendly`, `is_high_automation_risk`, `is_high_ai_adoption`, and `is_growth_projection`.
- `models/marts/`: analytical summary marts by job title, industry, location, and automation/AI adoption.

## How to Run

From the repository root, install dependencies:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

DBT was verified with Python 3.12 and `dbt-duckdb`. If your active virtualenv uses Python 3.14 and DBT fails during import, use a Python 3.12 or 3.13 environment for the DBT commands.

Make sure the Silver artifact exists:

```powershell
python projects/02-job-market-analytics/src/jobs/run_silver.py
```

Then run DBT from this directory:

```powershell
cd projects/02-job-market-analytics/dbt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

Using `uv`, the same local run can be executed without changing the main virtualenv:

```powershell
uv run --python 3.12 --with dbt-duckdb==1.10.1 dbt debug --profiles-dir .
uv run --python 3.12 --with dbt-duckdb==1.10.1 dbt run --profiles-dir .
uv run --python 3.12 --with dbt-duckdb==1.10.1 dbt test --profiles-dir .
```

## Relationship to Python Gold

The existing Python Gold v1 outputs under `../data/gold/` remain valid local artifacts. The DBT marts are a parallel SQL modeling path that formalizes those analytical summaries with DBT structure, documentation, and tests. This project should not be described as production-grade DBT yet; it is a realistic local analytics-engineering implementation.
