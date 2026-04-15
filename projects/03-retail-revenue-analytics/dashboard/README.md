# Retail Revenue Analytics Dashboard

Local React dashboard for the retail revenue analytics case study.

The dashboard consumes the existing read-only Flask API at `http://127.0.0.1:5002`. It does not read DuckDB directly, run DBT, rebuild marts, or calculate business KPIs in the browser.

## Prerequisites

From the repository root, make sure the upstream local artifacts exist:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
```

Build the DBT DuckDB marts:

```powershell
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 run
cd ../../..
```

Start the API:

```powershell
python projects/03-retail-revenue-analytics/api/app.py
```

Expected API URL:

```text
http://127.0.0.1:5002
```

## Configure

Copy `.env.example` to `.env` if you need to override the default API base URL:

```powershell
cd projects/03-retail-revenue-analytics/dashboard
Copy-Item .env.example .env
```

Default value:

```text
VITE_API_BASE_URL=http://127.0.0.1:5002
```

## Run

Install dependencies and start Vite:

```powershell
npm install
npm run dev
```

Expected dashboard URL:

```text
http://127.0.0.1:5173
```

## Build

```powershell
npm run build
```

The build runs TypeScript type-checking before creating the local Vite build output.

## Dashboard Scope

Implemented sections:

- KPI cards from `/api/v1/kpis`.
- Daily revenue trend from `/api/v1/daily-revenue`.
- Category performance from `/api/v1/category-performance`.
- Seller performance from `/api/v1/seller-performance`.
- Customer state performance from `/api/v1/customer-state-performance`.
- Order status summary from `/api/v1/order-status-summary`.
- Payment type summary from `/api/v1/payment-type-summary`.

The UI includes loading, empty, and endpoint-level error states. If the API is offline, the dashboard reports the unavailable API instead of showing mock analytics.

## Non-Goals

- No authentication or authorization.
- No cloud deployment.
- No write behavior.
- No direct DuckDB reads from the frontend.
- No production commerce UI claims.
- No accounting-grade revenue claims.
