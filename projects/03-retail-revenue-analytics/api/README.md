# Retail Revenue Analytics API

Small read-only Flask API over the local DuckDB DBT mart layer.

The API is intentionally thin:

- it reads existing DBT mart tables from DuckDB;
- it returns JSON-only responses;
- it does not run DBT;
- it does not rebuild transformation logic;
- it does not write data.

## Prerequisites

Build the local DuckDB marts first:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 run
cd ../../..
```

Expected DuckDB path:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

## Run Locally

From the repository root:

```powershell
python projects/03-retail-revenue-analytics/api/app.py
```

Default URL:

```text
http://127.0.0.1:5002
```

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

```powershell
Invoke-RestMethod http://127.0.0.1:5002/health
Invoke-RestMethod http://127.0.0.1:5002/api/v1/kpis
Invoke-RestMethod "http://127.0.0.1:5002/api/v1/daily-revenue?limit=10&order_status=delivered"
Invoke-RestMethod "http://127.0.0.1:5002/api/v1/category-performance?limit=10&sort_by=gross_merchandise_value"
Invoke-RestMethod "http://127.0.0.1:5002/api/v1/fct-sales?limit=10&customer_state=SP"
```

## Scope Notes

This API is a local analytical serving layer, not a production commerce backend. It does not implement authentication, authorization, caching, background jobs, orchestration, cloud deployment, or dashboard code.

Item-side revenue metrics come from the modeled `fct_sales` mart. Payment summaries describe payment behavior and should not be interpreted as item-level sales revenue.
