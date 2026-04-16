# DBT Layer

DBT is added after Bronze, Silver, and Gold v1 because the project now has stable source-aligned Silver CSV outputs that can support SQL modeling.

The DBT layer demonstrates dimensional modeling readiness as actual local SQL models. It does not replace the Python pipeline and does not introduce orchestration, serving APIs, dashboards, cloud infrastructure, or PostgreSQL requirements.

## Local-First DuckDB Path

DuckDB is the primary target for this phase.

DBT reads Silver CSV files from:

```text
data/silver/tables/
```

The local DuckDB database is written to:

```text
data/retail_revenue_analytics.duckdb
```

## Project Layout

```text
dbt/
  models/
    staging/
    intermediate/
    marts/
  tests/
  scripts/
```

## Sources

DBT defines sources for the Silver tables:

- `orders`
- `order_items`
- `order_payments`
- `products`
- `product_category_name_translation`
- `customers`
- `sellers`

These are trusted standardized inputs from the Python Silver layer, not raw Bronze files.

## Model Organization

Staging models preserve source-aligned grain and expose stable analytical columns.

Intermediate models prepare reusable modeling structures:

- `int_order_items_enriched`: one row per order item, with order, product, category, customer, seller, and date context.
- `int_order_payments_summary`: one row per order, with payment rows aggregated before they can be joined downstream.

Mart models materialize as DuckDB tables:

- dimensions: `dim_date`, `dim_product`, `dim_customer`, `dim_seller`, `dim_store`, and `dim_salesperson`;
- `fct_sales`;
- business summary marts.

## Tests

Implemented DBT tests include:

- `not_null` tests for key identifiers and important measures;
- `unique` tests where the model grain is clear;
- relationship tests between order items, orders, products, customers, sellers, stores, salespeople, and dates;
- accepted values tests for the observed `order_status` domain;
- singular tests for sales fact row preservation, non-negative item-side sales measures, non-negative payments, valid purchase dates, and order-grain payment summaries.

## Run Commands

From the repository root:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

The script uses:

```powershell
uv run --python 3.12 --with-requirements requirements.txt python -m dbt.cli.main ...
```
