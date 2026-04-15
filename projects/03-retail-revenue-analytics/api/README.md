# Retail Revenue Analytics API

Small read-only Flask API over the local DuckDB DBT mart layer.

The API is intentionally thin:

- it reads existing DBT mart tables from DuckDB;
- it returns JSON-only responses;
- it does not run DBT;
- it does not rebuild transformation logic;
- it does not write data.

## Prerequisites

Build the local DuckDB marts first. For a clean local setup from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r projects/03-retail-revenue-analytics/dbt/requirements.txt
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
(cd projects/03-retail-revenue-analytics/dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb)
```

Expected DuckDB path:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

## Run Locally

From the repository root:

```bash
python projects/03-retail-revenue-analytics/api/app.py
```

Default URL:

```text
http://127.0.0.1:5002
```

The local API is HTTP-only. Do not use `https://127.0.0.1:5002`.

## Run With Docker

From the project directory:

```bash
cd projects/03-retail-revenue-analytics
docker compose up --build retail-api
```

The API container:

- listens on `0.0.0.0:5002` inside Docker;
- publishes `5002:5002` to the host;
- reads the DuckDB mart database from the bind-mounted `./data` directory;
- expects the mounted database at
  `/workspace/projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb`.

The image does not include generated data. Build the DuckDB file first or mount an existing local `data/` directory.
Docker is a demo path here, not a requirement for local API work.

## Local Dashboard CORS

The API allows explicit CORS origins through `RETAIL_REVENUE_API_CORS_ALLOWED_ORIGINS`.
The default list includes common Vite origins:

```text
http://127.0.0.1:4173
http://localhost:4173
http://127.0.0.1:5173
http://localhost:5173
http://127.0.0.1:5174
http://localhost:5174
http://127.0.0.1:5175
http://localhost:5175
http://127.0.0.1:5179
http://localhost:5179
```

For local development, `RETAIL_REVENUE_API_ALLOW_LOCAL_DEV_CORS=true` also allows HTTP `localhost` and `127.0.0.1` origins on Vite-style ports from `5173` through `5199`. This is local-development behavior only; it is not a production CORS policy.

Directly opening `/health` in a browser is not the same as a dashboard `fetch` request. The browser can load `/health` directly while still blocking dashboard requests if CORS does not allow the Vite origin.

## Endpoints

- `GET /health`
- `GET /api/v1`
- `GET /api/v1/kpis`
- `GET /api/v1/daily-revenue`
- `GET /api/v1/category-performance`
- `GET /api/v1/seller-performance`
- `GET /api/v1/customer-state-performance`
- `GET /api/v1/order-status-summary`
- `GET /api/v1/payment-type-summary`
- `GET /api/v1/fct-sales`

## Example Requests

```bash
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5002/api/v1/kpis
curl "http://127.0.0.1:5002/api/v1/daily-revenue?limit=10&order_status=delivered"
curl "http://127.0.0.1:5002/api/v1/category-performance?limit=10&sort_by=gross_merchandise_value"
curl "http://127.0.0.1:5002/api/v1/fct-sales?limit=10&customer_state=SP"
```

## Scope Notes

This API is a local analytical serving layer, not a production commerce backend. It does not implement authentication, authorization, caching, background jobs, orchestration, cloud deployment, or dashboard code.

Item-side revenue metrics come from the modeled `fct_sales` mart. Payment summaries describe payment behavior and should not be interpreted as item-level sales revenue.

## Troubleshooting

Wrong local API URL:

```text
https://127.0.0.1:5002
```

Right local API URL:

```text
http://127.0.0.1:5002
```

If the dashboard says the API is unavailable:

- Confirm the Flask API is running.
- Confirm `VITE_API_BASE_URL` uses `http://`.
- Confirm the dashboard origin is listed in `RETAIL_REVENUE_API_CORS_ALLOWED_ORIGINS` or is an allowed local dev origin.

For the Docker-assisted path, also confirm:

- the `retail-api` container is running;
- `./data/retail_revenue_analytics.duckdb` exists on the host;
- the bind mount is present inside the container.

If mart-backed endpoints return `503` or `/health` reports a degraded state, rebuild the DuckDB marts first.
