# Retail Revenue Analytics DBT

This directory contains the DBT modeling layer for the retail revenue analytics project.

The implementation is local-first and uses DuckDB as the primary target. DBT reads the source-aligned Silver CSV outputs produced by the Python Silver pipeline and builds dimensional marts for portfolio inspection.

DBT does not replace the Python Bronze, Silver, or Gold path. It adds an analytics-engineering modeling layer on top of Silver.

## Source Strategy

DBT reads local Silver CSV files from:

```text
../data/silver/tables/
```

The local DuckDB database is written to:

```text
../data/retail_revenue_analytics.duckdb
```

The Silver table path can be overridden at runtime:

```powershell
.\scripts\run_dbt_duckdb.ps1 run --vars "{silver_tables_path: '../data/silver/tables'}"
```

## Model Layers

- `models/staging/`: source-aligned staging models over Silver CSV files.
- `models/intermediate/`: reusable preparation models for item-grain sales context and order-grain payment summaries.
- `models/marts/`: dimensional models, fact-like sales model, and business-friendly summary marts.

Staging and intermediate models are ephemeral. Mart models materialize as DuckDB tables.

## Implemented Marts

Dimensions:

- `dim_product`
- `dim_customer`
- `dim_seller`
- `dim_date`

Fact-like mart:

- `fct_sales`

Business summary marts:

- `mart_daily_revenue`
- `mart_category_performance`
- `mart_seller_performance`
- `mart_customer_state_performance`
- `mart_order_status_summary`
- `mart_payment_type_summary`

## Run DuckDB Path

From the repository root, generate Silver first:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
```

Then run DBT from this directory:

```powershell
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Equivalent manual command:

```powershell
uv run --python 3.12 --with-requirements requirements.txt python -m dbt.cli.main run --profiles-dir . --target duckdb
```

## Tests

DBT tests cover:

- not-null checks on key identifiers and measures;
- uniqueness tests where model grain is clear;
- relationship tests from orders/items/payments to their parent entities;
- accepted values for observed `order_status` values;
- singular tests that verify `fct_sales` preserves order item grain and has no negative item-side sales measures.

## Revenue Caveat

`fct_sales` is an analytical sales fact-like mart at order item grain. It uses:

```text
gross_merchandise_value = item_price + freight_value
```

Payment rows are aggregated to order grain before they are joined to item rows. Payment fields in `fct_sales` are order-level context and can repeat across multi-item orders. They should not be summed as item-level revenue.

This DBT layer is not an accounting-grade revenue ledger and does not implement refunds, cancellations, chargebacks, or settlement reconciliation.
