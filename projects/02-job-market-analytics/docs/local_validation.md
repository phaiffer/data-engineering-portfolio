# Local Validation Guide

This guide gives reviewers a lightweight validation path for project 02 on Windows PowerShell.

Run commands from the repository root unless a section says otherwise.

## Prerequisites

Python environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

dbt runtime:

```powershell
uv --version
```

The dbt helper scripts use `uv` with Python 3.12 and `projects/02-job-market-analytics/dbt/requirements.txt`.

PostgreSQL path:

```powershell
Copy-Item projects/02-job-market-analytics/.env.example projects/02-job-market-analytics/.env
```

Then update the PostgreSQL password and database settings in `.env` as needed.

## 1. Build the Local Medallion Artifacts

For a full refresh:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
python projects/02-job-market-analytics/src/jobs/run_silver.py
python projects/02-job-market-analytics/src/jobs/run_gold.py
```

For dbt review, the critical artifact is:

```text
projects/02-job-market-analytics/data/silver/ai_job_market_insights_silver.csv
```

## 2. Validate the DuckDB dbt Path

Recommended wrapper:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
```

Manual commands:

```powershell
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
cd ../../..
```

Expected result:

- `debug` connects with the `duckdb` target.
- `run` builds the dbt marts into the local DuckDB database.
- `test` passes source, model, and singular tests.
- `projects/02-job-market-analytics/data/job_market_analytics.duckdb` exists.

## 3. Validate the PostgreSQL dbt Path

Recommended wrapper:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

Manual commands:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
cd ../../..
```

Expected result:

- Silver loads into `analytics.job_market_insights_silver`.
- `debug` connects with the `postgres` target.
- `run` builds the dbt marts into the configured marts schema.
- `test` passes source, model, and singular tests.

## 4. Inspect PostgreSQL Marts

Use `psql`, pgAdmin, DBeaver, or another PostgreSQL client.

Basic row-count checks:

```sql
select count(*) as silver_records
from analytics.job_market_insights_silver;

select count(*) as job_title_rows
from marts.mart_job_title_summary;

select count(*) as industry_rows
from marts.mart_industry_summary;

select count(*) as location_rows
from marts.mart_location_summary;

select count(*) as automation_ai_rows
from marts.mart_automation_ai_summary;
```

Portfolio-friendly spot checks:

```sql
select job_title, total_records, average_salary_usd
from marts.mart_job_title_summary
order by average_salary_usd desc
limit 10;

select industry, total_records, high_ai_adoption_share, high_automation_risk_share
from marts.mart_industry_summary
order by total_records desc
limit 10;

select automation_risk, ai_adoption_level, total_records, average_salary_usd
from marts.mart_automation_ai_summary
order by total_records desc;
```

## 5. Validate the API

Start the API:

```powershell
.\projects\02-job-market-analytics\scripts\start_api.ps1
```

Check health:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/health
```

Check primary endpoints:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/api/v1/kpis
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/job-titles?limit=5&order_by=average_salary_usd&direction=desc"
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/industries?limit=5"
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/locations?limit=5"
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/automation-ai?limit=5"
```

Expected result:

- `/health` returns `status: ok` when PostgreSQL is reachable.
- List endpoints return JSON with a `data` array.
- Invalid query parameters return controlled JSON errors instead of stack traces.

## 6. Validate the Dashboard

Start the API first, then open a second terminal:

```powershell
.\projects\02-job-market-analytics\scripts\start_dashboard.ps1
```

Open the local Vite URL, usually:

```text
http://localhost:5173
```

For screenshot capture:

```text
http://127.0.0.1:5173/?capture=1
```

Expected result:

- The API status badge is healthy.
- KPI, job title, industry, location, and automation/AI sections load from API data.
- No dashboard section depends on hardcoded analytical rows.

## Troubleshooting Notes

- If DuckDB dbt fails before connecting, confirm `uv` is installed and can create a Python 3.12 runtime.
- If PostgreSQL dbt cannot connect, confirm `JOB_MARKET_POSTGRES_*` values in `.env`.
- If the API health endpoint returns `503`, validate PostgreSQL is running and the marts exist.
- If the dashboard cannot reach the API, confirm `JOB_MARKET_API_CORS_ALLOWED_ORIGINS` includes the Vite origin.
