# dbt Path Comparison

Project 02 uses one dbt project with two execution targets. The models are shared; the source runtime changes.

## Why There Are Two Paths

The DuckDB path makes the SQL models easy to run locally from a file artifact. It is the fastest way to review the staging, intermediate, mart, and test logic without requiring a database server.

The PostgreSQL path proves that the same modeling logic can be materialized into relational marts that support the API and dashboard. It is the serving path for the implemented read layer.

This keeps the project local-first while still showing both analytical development and relational serving behavior.

## Quick Comparison

| Area | DuckDB path | PostgreSQL path |
| --- | --- | --- |
| dbt target | `duckdb` | `postgres` |
| Source | `../data/silver/ai_job_market_insights_silver.csv` | `analytics.job_market_insights_silver` |
| Load step | None after Silver CSV exists | `src/jobs/run_postgres_load.py` |
| Output | `data/job_market_analytics.duckdb` | `marts` schema tables |
| Main value | Fast SQL model validation | API/dashboard serving validation |
| Reviewer use | Inspect model logic quickly | Confirm relational marts and read layer |

## DuckDB Path

Flow:

```text
Silver CSV
-> dbt external CSV source
-> staging
-> intermediate
-> marts
-> local DuckDB database
```

Run from the repository root:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
```

Run lower-level commands from `projects/02-job-market-analytics/dbt`:

```powershell
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Inspect this path when you want to review SQL modeling without PostgreSQL setup.

## PostgreSQL Path

Flow:

```text
Silver CSV
-> analytics.job_market_insights_silver
-> dbt PostgreSQL source
-> staging
-> intermediate
-> marts
-> Flask API
-> React dashboard
```

Run from the repository root:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

Run lower-level commands manually:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

Inspect this path when you want to validate the database tables used by the API and dashboard.

## Shared Model Tree

Both paths use the same dbt models:

- `models/staging/stg_job_market_insights.sql`
- `models/intermediate/int_job_market_enriched.sql`
- `models/marts/mart_job_title_summary.sql`
- `models/marts/mart_industry_summary.sql`
- `models/marts/mart_location_summary.sql`
- `models/marts/mart_automation_ai_summary.sql`

This is the main review point: the transformation logic is not duplicated for each runtime.

## Artifact Expectations

After the DuckDB path:

```text
data/job_market_analytics.duckdb
```

After the PostgreSQL path:

```text
analytics.job_market_insights_silver
marts.mart_job_title_summary
marts.mart_industry_summary
marts.mart_location_summary
marts.mart_automation_ai_summary
```

## Reviewer Notes

- Review DuckDB first when you want the fastest SQL/dbt proof.
- Review PostgreSQL when validating the serving story.
- The API and dashboard depend on the PostgreSQL path, not the DuckDB artifact.
- Python Gold remains useful as a medallion artifact, but dbt marts are the stronger SQL review surface.
