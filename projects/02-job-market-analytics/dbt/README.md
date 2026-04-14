# Job Market Analytics DBT

This directory contains the DBT modeling layer for the job market analytics project.

The DBT implementation is intentionally local and portfolio-oriented. It supports two targets over the same staging, intermediate, and mart model tree:

- DuckDB: local modeling directly from the standardized Silver CSV.
- PostgreSQL: relational modeling over a Silver table loaded from the same CSV.

DBT does not read raw Bronze data directly, create serving views, or replace the Python Gold v1 artifacts yet.

## Source Strategy

### Path A: DuckDB

```text
../data/silver/ai_job_market_insights_silver.csv
```

DBT reads the local Silver CSV as `duckdb_silver.ai_job_market_insights_silver` using DuckDB external CSV support. The local DuckDB database is written to:

```text
../data/job_market_analytics.duckdb
```

The Silver path can be overridden at runtime:

```powershell
dbt run --profiles-dir . --vars "{silver_dataset_path: '../data/silver/ai_job_market_insights_silver.csv'}"
```

### Path B: PostgreSQL

The PostgreSQL path first loads the same Silver CSV into:

```text
analytics.job_market_insights_silver
```

DBT then reads that relational source as `postgres_silver.job_market_insights_silver` and builds the same staging, intermediate, and mart models against PostgreSQL.

This keeps DBT focused on SQL modeling over the already standardized Silver contract in both paths:

- Silver v1 remains the row-preserving Python output.
- DBT staging keeps the same row grain and casts fields for SQL modeling.
- DBT intermediate models add only source-supported reusable flags.
- DBT marts formalize the same analytical grains used by Python Gold v1.

## Model Layers

- `models/staging/`: source-aligned DBT staging over the Silver artifact or loaded Silver table.
- `models/intermediate/`: row-level enrichment flags such as `is_remote_friendly`, `is_high_automation_risk`, `is_high_ai_adoption`, and `is_growth_projection`.
- `models/marts/`: analytical summary marts by job title, industry, location, and automation/AI adoption.

## Install DBT Dependencies

From this DBT directory:

```powershell
python -m pip install -r requirements.txt
```

DBT was verified with Python 3.12 and `dbt-duckdb`/`dbt-postgres`. If your active virtualenv uses Python 3.14 and DBT fails during import, use a Python 3.12 or 3.13 environment for DBT commands.

Using `uv`, you can run DBT without changing the main virtualenv:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir .
```

## Run DuckDB Path

Make sure the Silver artifact exists:

```powershell
python ../src/jobs/run_silver.py
```

Run DBT with the DuckDB target:

```powershell
dbt debug --profiles-dir . --target dev
dbt run --profiles-dir . --target dev
dbt test --profiles-dir . --target dev
```

Using `uv`:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir . --target dev
uv run --python 3.12 --with-requirements requirements.txt dbt run --profiles-dir . --target dev
uv run --python 3.12 --with-requirements requirements.txt dbt test --profiles-dir . --target dev
```

## Run PostgreSQL Path

Configure project-local PostgreSQL connection variables in `../.env`:

```text
JOB_MARKET_POSTGRES_HOST=localhost
JOB_MARKET_POSTGRES_PORT=5432
JOB_MARKET_POSTGRES_DB=job_market_analytics
JOB_MARKET_POSTGRES_USER=postgres
JOB_MARKET_POSTGRES_PASSWORD=postgres
JOB_MARKET_DBT_SCHEMA=analytics_dbt
```

Load Silver into PostgreSQL from the repository root:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
```

Then run DBT from this directory:

```powershell
dbt debug --profiles-dir . --target postgres
dbt run --profiles-dir . --target postgres
dbt test --profiles-dir . --target postgres
```

Using `uv`:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir . --target postgres
uv run --python 3.12 --with-requirements requirements.txt dbt run --profiles-dir . --target postgres
uv run --python 3.12 --with-requirements requirements.txt dbt test --profiles-dir . --target postgres
```

For a quick row-count check after loading PostgreSQL:

```sql
select count(*) from analytics.job_market_insights_silver;
```

After running each DBT target, a simple consistency check is to compare the row counts in `stg_job_market_insights` and the summed `total_records` in each mart across DuckDB and PostgreSQL. These should match when both targets read the same Silver artifact.

## Relationship to Python Gold

The existing Python Gold v1 outputs under `../data/gold/` remain valid local artifacts. The DBT marts are parallel SQL modeling paths that formalize those analytical summaries with DBT structure, documentation, and tests. This project should not be described as production-grade DBT yet; it is a realistic local analytics-engineering implementation.
