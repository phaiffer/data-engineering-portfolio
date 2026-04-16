# Job Market Analytics DBT

This directory contains the DBT modeling layer for the job market analytics project.

The DBT implementation is intentionally local and portfolio-oriented. It supports two targets over the same staging, intermediate, and mart model tree:

- DuckDB: local modeling directly from the standardized Silver CSV.
- PostgreSQL: relational modeling over a Silver table loaded from the same CSV.

DBT does not read raw Bronze data directly, create serving views, or replace the Python Gold v1 artifacts yet.

For a reviewer-oriented comparison of the two paths, see [`../docs/dbt_path_comparison.md`](../docs/dbt_path_comparison.md). For end-to-end local checks, see [`../docs/local_validation.md`](../docs/local_validation.md).

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
.\scripts\run_dbt_duckdb.ps1 run --vars "{silver_dataset_path: '../data/silver/ai_job_market_insights_silver.csv'}"
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
- DBT staging and intermediate models are ephemeral to avoid noisy local schemas.
- DBT marts formalize the same analytical grains used by Python Gold v1.

## Model Layers

- `models/staging/`: ephemeral, source-aligned DBT staging over the Silver artifact or loaded Silver table.
- `models/intermediate/`: ephemeral row-level enrichment flags such as `is_remote_friendly`, `is_high_automation_risk`, `is_high_ai_adoption`, and `is_growth_projection`.
- `models/marts/`: table materializations for analytical summaries by job title, industry, location, and automation/AI adoption.

For PostgreSQL, the intended schema structure is:

- `analytics.job_market_insights_silver`: loaded Silver source table.
- `marts.mart_job_title_summary`: final DBT mart.
- `marts.mart_industry_summary`: final DBT mart.
- `marts.mart_location_summary`: final DBT mart.
- `marts.mart_automation_ai_summary`: final DBT mart.

## Supported DBT Runtime

Do not use the repository base `.venv` as the supported DBT runtime if it is on an incompatible Python version. The current local failure mode is an import-time DBT dependency error before any database connection is attempted.

Use the PowerShell helper scripts in `scripts/`. They run DBT through `uv` with Python 3.12 and the DBT-specific dependency file in this directory:

```powershell
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_postgres.ps1 debug
```

The helper scripts use:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt ...
```

You can also run that command manually from this DBT directory:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir . --target duckdb
```

## Run DuckDB Path

Make sure the Silver artifact exists:

```powershell
python ../src/jobs/run_silver.py
```

Run DBT with the DuckDB target:

```powershell
..\scripts\validate_dbt_duckdb.ps1
```

Or run from this DBT directory:

```powershell
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Equivalent manual `uv` commands:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir . --target duckdb
uv run --python 3.12 --with-requirements requirements.txt dbt run --profiles-dir . --target duckdb
uv run --python 3.12 --with-requirements requirements.txt dbt test --profiles-dir . --target duckdb
```

## Run PostgreSQL Path

Configure project-local PostgreSQL connection variables in `../.env`:

```text
JOB_MARKET_POSTGRES_HOST=localhost
JOB_MARKET_POSTGRES_PORT=5432
JOB_MARKET_POSTGRES_DB=job_market_analytics
JOB_MARKET_POSTGRES_USER=postgres
JOB_MARKET_POSTGRES_PASSWORD=postgres
JOB_MARKET_DBT_SCHEMA=marts
```

Load Silver into PostgreSQL from the repository root:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
```

Then run DBT from this directory:

```powershell
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

From the repository root, the wrapper below runs the Silver PostgreSQL load plus `debug`, `run`, and `test`:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

The PostgreSQL helper loads `JOB_MARKET_*` variables from `../.env` into the current DBT process before invoking `uv`.

Equivalent manual `uv` commands, after setting the `JOB_MARKET_*` variables in the current shell:

```powershell
uv run --python 3.12 --with-requirements requirements.txt dbt debug --profiles-dir . --target postgres
uv run --python 3.12 --with-requirements requirements.txt dbt run --profiles-dir . --target postgres
uv run --python 3.12 --with-requirements requirements.txt dbt test --profiles-dir . --target postgres
```

For a quick row-count check after loading PostgreSQL:

```sql
select count(*) from analytics.job_market_insights_silver;
```

After `.\scripts\run_dbt_postgres.ps1 run`, the final marts should exist in the `marts` schema:

```sql
select count(*) from marts.mart_job_title_summary;
select count(*) from marts.mart_industry_summary;
select count(*) from marts.mart_location_summary;
select count(*) from marts.mart_automation_ai_summary;
```

After running each DBT target, a simple consistency check is to compare the row counts in `stg_job_market_insights` and the summed `total_records` in each mart across DuckDB and PostgreSQL. These should match when both targets read the same Silver artifact.

## Relationship to Python Gold

The existing Python Gold v1 outputs under `../data/gold/` remain valid local artifacts. The DBT marts are parallel SQL modeling paths that formalize those analytical summaries with DBT structure, documentation, and tests. This project should not be described as production-grade DBT yet; it is a realistic local analytics-engineering implementation.
