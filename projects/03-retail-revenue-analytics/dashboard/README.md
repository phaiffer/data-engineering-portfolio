# Retail Revenue Analytics Dashboard

Local React dashboard for the retail revenue analytics case study.

The dashboard consumes the existing read-only Flask API at `http://127.0.0.1:5002`. It does not read DuckDB directly, run DBT, rebuild marts, or calculate business KPIs in the browser.

## Prerequisites

From the repository root, make sure the upstream local artifacts exist:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r projects/03-retail-revenue-analytics/dbt/requirements.txt
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
```

`run_gold.py` is part of the full manual pipeline, but it is not required to render the dashboard. Build the DBT DuckDB marts:

```bash
(cd projects/03-retail-revenue-analytics/dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb)
```

Start the API:

```bash
python projects/03-retail-revenue-analytics/api/app.py
```

Expected API URL:

```text
http://127.0.0.1:5002
```

The local Flask API is HTTP-only. `https://127.0.0.1:5002` will fail with an SSL protocol error.

## Configure

Copy `.env.example` to `.env` if you need to override the default API base URL:

```bash
cd projects/03-retail-revenue-analytics/dashboard
cp .env.example .env
```

Default value:

```text
VITE_API_BASE_URL=http://127.0.0.1:5002
```

Use `http://`, not `https://`, for the local API. The dashboard validates the common bad local HTTPS URLs and shows a clear error in the UI.

## Run

Install dependencies and start Vite:

```bash
npm install
npm run dev
```

Expected dashboard URL:

```text
http://127.0.0.1:5173
```

Vite may choose another local port if `5173` is already in use. The API allows common local Vite origins and HTTP `localhost` or `127.0.0.1` ports from `5173` through `5199` when local-dev CORS is enabled.

## Run With Docker

From the project directory:

```bash
cd projects/03-retail-revenue-analytics
docker compose up --build retail-api retail-dashboard
```

Expected Docker-assisted URLs:

```text
API:       http://127.0.0.1:5002
Dashboard: http://127.0.0.1:4173
```

The Docker dashboard path builds static assets and serves them from a lightweight container. The browser-facing API URL is baked in at build time through `VITE_API_BASE_URL`, so rebuild the dashboard image if you change that URL.
Docker improves demo packaging, but it is not required for frontend development.

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

## Troubleshooting

Opening `http://127.0.0.1:5002/health` directly in a browser only proves the API route is reachable. It does not prove browser `fetch` from the dashboard origin is allowed. CORS can still block dashboard requests.

Wrong:

```text
VITE_API_BASE_URL=https://127.0.0.1:5002
```

Right:

```text
VITE_API_BASE_URL=http://127.0.0.1:5002
```

If the dashboard says the API is unavailable:

- Check that the Flask API is running.
- Check that `VITE_API_BASE_URL` uses `http://`.
- Check the current dashboard origin shown in the header.
- Check that the API allows that local Vite origin through CORS.

For the Docker-assisted path, also check:

- the dashboard was built with `http://127.0.0.1:5002` or another host-reachable API URL;
- the API container is listening on host port `5002`;
- the current browser origin is `http://127.0.0.1:4173` or `http://localhost:4173`.

If the API health route is degraded or mart-backed endpoints return `503`, rebuild the DuckDB marts before retrying the dashboard.

## Non-Goals

- No authentication or authorization.
- No cloud deployment.
- No write behavior.
- No direct DuckDB reads from the frontend.
- No production commerce UI claims.
- No accounting-grade revenue claims.
