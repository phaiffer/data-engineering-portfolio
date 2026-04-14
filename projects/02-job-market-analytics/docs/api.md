# API Layer - Flask

The Flask API exposes the project 02 PostgreSQL Silver table and DBT marts for
local dashboard consumption.

This is a thin read-only analytics API. It does not rebuild Bronze, Silver,
Gold, or DBT logic, and it does not provide authentication or write endpoints.

## Source Tables

The API reads only from:

- `analytics.job_market_insights_silver`
- `marts.mart_job_title_summary`
- `marts.mart_industry_summary`
- `marts.mart_location_summary`
- `marts.mart_automation_ai_summary`

`analytics.job_market_insights_silver` is used for whole-dataset KPIs. The
`marts` tables are used for dashboard section rows.

## Prerequisites

Configure `projects/02-job-market-analytics/.env` with PostgreSQL settings:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=job_market_analytics
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
POSTGRES_ANALYTICS_SCHEMA=analytics
POSTGRES_MARTS_SCHEMA=marts
POSTGRES_SILVER_TABLE=job_market_insights_silver
```

Load the Silver table and build the PostgreSQL marts:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

## How to Run Locally

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe projects/02-job-market-analytics/api/app.py
```

If your virtual environment is already activated:

```powershell
python projects/02-job-market-analytics/api/app.py
```

By default, the API runs at:

```text
http://127.0.0.1:5001
```

Optional local API settings can be added to `.env`:

```text
JOB_MARKET_API_SERVICE_NAME=job-market-analytics-api
JOB_MARKET_API_HOST=127.0.0.1
JOB_MARKET_API_PORT=5001
JOB_MARKET_API_DEBUG=false
JOB_MARKET_API_CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
```

## Endpoints

### `GET /health`

Returns service health and a lightweight PostgreSQL connectivity check.

```json
{
  "data": {
    "service": "job-market-analytics-api",
    "status": "ok",
    "database": "ok",
    "source": "marts DBT schema over PostgreSQL"
  }
}
```

If PostgreSQL is unavailable, the endpoint returns `503` with `status:
degraded`.

### `GET /api/v1/kpis`

Returns whole-dataset KPIs derived from
`analytics.job_market_insights_silver`.

```json
{
  "data": {
    "total_records": 500,
    "average_salary_usd": 98234.5,
    "median_salary_usd": 97000,
    "remote_friendly_share": 0.42,
    "high_ai_adoption_share": 0.31,
    "high_automation_risk_share": 0.18,
    "growth_projection_share": 0.56
  }
}
```

### `GET /api/v1/job-titles`

Returns rows from `marts.mart_job_title_summary`.

### `GET /api/v1/industries`

Returns rows from `marts.mart_industry_summary`.

### `GET /api/v1/locations`

Returns rows from `marts.mart_location_summary`.

### `GET /api/v1/automation-ai`

Returns rows from `marts.mart_automation_ai_summary`.

The legacy first-dashboard aliases are also available:

- `GET /api/v1/job-title-summary`
- `GET /api/v1/industry-summary`
- `GET /api/v1/location-summary`
- `GET /api/v1/automation-ai-summary`

## Query Parameters

The list endpoints support safe optional query parameters:

- `limit`: integer from `1` to `1000`
- `order_by`: whitelisted column for that endpoint's mart
- `direction`: `asc` or `desc`

Example:

```text
http://127.0.0.1:5001/api/v1/job-titles?order_by=average_salary_usd&limit=10&direction=desc
```

The API does not concatenate raw user input into SQL. Table names are fixed,
ordering columns are whitelisted, and SQL identifiers are built with
`psycopg.sql`.

## Error Handling

Database failures return JSON with a `503` status code and a generic error
message. Stack traces are logged locally but are not returned in HTTP
responses.

Invalid query parameters return JSON with a `400` status code.

Unknown routes return JSON through the shared Flask error handler.

## CORS

The API adds minimal local-development CORS headers for configured local
origins. By default, it allows the Vite development origins:

```text
http://127.0.0.1:5173
http://localhost:5173
```

## Portfolio Story

Project 02 now demonstrates a local analytical serving path:

```text
Python medallion pipeline
-> DBT analytical modeling
-> PostgreSQL-backed marts
-> read-only Flask analytics API
-> React dashboard
```
