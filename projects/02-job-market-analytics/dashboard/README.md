# Job Market Analytics Dashboard

React, Vite, and TypeScript dashboard for the job-market analytics portfolio case.

The dashboard is visually aligned with the Figma concept, and all main dashboard reads come from the local project 02 Flask API instead of mock values.

## Read Path

The browser consumes the read-only local Flask API in `../api/`.

The API reads from PostgreSQL:

- `analytics.job_market_insights_silver` for dashboard KPIs.
- `marts.mart_job_title_summary` for role salary ranking.
- `marts.mart_industry_summary` for the hero chart and Industry Deep Dive table.
- `marts.mart_location_summary` for location salary ranking.
- `marts.mart_automation_ai_summary` for AI adoption and automation-risk analysis.

No frontend logic rebuilds Bronze, Silver, Gold, or DBT transformations.

Dashboard sections map to these API endpoints:

- KPI row: `GET /api/v1/kpis`
- Job title chart: `GET /api/v1/job-titles`
- Industry chart and table: `GET /api/v1/industries`
- Location chart: `GET /api/v1/locations`
- Automation vs AI chart: `GET /api/v1/automation-ai`
- API status badge: `GET /health`

## Environment

Create a local `.env` from the example:

```powershell
Copy-Item .env.example .env
```

Default API URL:

```text
VITE_API_BASE_URL=http://127.0.0.1:5001
```

## Install

From this directory:

```powershell
npm install
```

## Run Locally

Start the stack in this order:

1. PostgreSQL with the validated project 02 marts available.
2. The read-only Flask API.
3. The Vite dashboard.

From the repository root, start the API:

```powershell
.\.venv\Scripts\python.exe projects/02-job-market-analytics/api/app.py
```

Then start the dashboard:

```powershell
cd projects/02-job-market-analytics/dashboard
npm run dev
```

Vite will print the local dashboard URL, usually:

```text
http://localhost:5173
```

## Build

```powershell
npm run build
```
