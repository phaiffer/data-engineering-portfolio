# Job Market Analytics API

Small read-only Flask API for the project 02 dashboard path.

The API reads from PostgreSQL only:

- `analytics.job_market_insights_silver` for whole-dataset KPI metrics.
- `marts.mart_job_title_summary`
- `marts.mart_industry_summary`
- `marts.mart_location_summary`
- `marts.mart_automation_ai_summary`

Run it from the repository root after loading Silver into PostgreSQL and running
DBT with the PostgreSQL target:

```powershell
.\projects\02-job-market-analytics\scripts\start_api.ps1
```

Equivalent direct command:

```powershell
.\.venv\Scripts\python.exe projects/02-job-market-analytics/api/app.py
```

By default it listens on:

```text
http://127.0.0.1:5001
```

Primary endpoints:

- `GET /health`
- `GET /api/v1/kpis`
- `GET /api/v1/job-titles`
- `GET /api/v1/industries`
- `GET /api/v1/locations`
- `GET /api/v1/automation-ai`

The list endpoints support safe `limit`, `order_by`, and `direction` query
parameters.

Quick PowerShell checks:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/health
Invoke-RestMethod http://127.0.0.1:5001/api/v1/kpis
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/job-titles?limit=5&order_by=average_salary_usd&direction=desc"
```
