# Retail Revenue Analytics

Retail and e-commerce analytics case study using the Kaggle dataset `olistbr/brazilian-ecommerce`.

This is the third portfolio case in the repository. It implements a local Bronze layer, source-aligned Silver tables, cautious Python Gold v1 KPI summaries, and DBT DuckDB dimensional marts. The project remains local-first and portfolio-oriented, with no production maturity claims.

## Why This Case Exists

The repository already contains:

- `01-hospital-analytics`: a hospital operations analytics case with serving-oriented outputs.
- `02-job-market-analytics`: a job market analytics case with Python processing, DBT marts, API, and dashboard layers.

This third case adds a retail marketplace domain with stronger dimensional modeling emphasis. It shows how a multi-table source can move from raw files to source-aligned Silver tables, then into fact, dimension, and mart-style SQL models.

The project proves:

- source-aware Silver design;
- careful order, item, payment, product, customer, and seller relationships;
- item-grain sales modeling;
- payment duplication avoidance;
- DBT as a local modeling and testing layer;
- a clean path toward future orchestration or serving layers without adding them prematurely.

## Dataset Choice

This project uses the Olist Brazilian E-Commerce Public Dataset from Kaggle:

- Kaggle handle: `olistbr/brazilian-ecommerce`
- Local raw folder name: `olist_brazilian_ecommerce`

Olist is a strong fit because it has multiple related CSV files instead of one flat sales table. The landed dataset includes orders, order items, payments, products, category translations, customers, sellers, reviews, and geolocation.

## Current Architecture Flow

```text
Kaggle dataset
-> Bronze raw landing and profiling
-> Silver source-aligned standardized tables
-> Gold Python KPI summaries
-> DBT DuckDB staging/intermediate/marts
-> future orchestration / serving / API / dashboard
```

## Implemented Layers

### Bronze

Bronze lands the Olist dataset locally, inventories all raw files, profiles the largest supported CSV with Pandas, and writes metadata.

The largest-CSV profiling rule is only a raw-stage convenience. It is not a final fact-grain decision.

### Silver

Silver v1 produces one source-aligned CSV per selected core table:

```text
orders
order_items
order_payments
products
product_category_name_translation
customers
sellers
```

Silver preserves each source table grain. It applies safe standardization only and does not aggregate, deduplicate, create surrogate keys, or join everything into one canonical table.

### Python Gold v1

Python Gold v1 produces first-pass revenue and business KPI summaries as CSV files. It uses item-side measures from `order_items` and summarizes payments separately by payment type.

### DBT DuckDB Marts

DBT reads the Silver CSV outputs and builds:

Dimensions:

- `dim_product`
- `dim_customer`
- `dim_seller`
- `dim_date`

Fact-like mart:

- `fct_sales`

Business marts:

- `mart_daily_revenue`
- `mart_category_performance`
- `mart_seller_performance`
- `mart_customer_state_performance`
- `mart_order_status_summary`
- `mart_payment_type_summary`

The DBT path is DuckDB-first and local. It does not require PostgreSQL in this phase.

## Revenue And Grain Rules

The central sales grain is one row per `order_id` and `order_item_id`.

Item-side measures:

- `item_price = order_items.price`
- `freight_value = order_items.freight_value`
- `gross_merchandise_value = item_price + freight_value`

Raw payment rows are not joined directly to item rows. DBT aggregates payments to one row per order before adding payment context to `fct_sales`.

Payment fields in `fct_sales` are order-level context. They can repeat across multi-item orders and should not be summed as item-level sales revenue.

## Documentation

- [Bronze layer](docs/bronze.md)
- [Source tables](docs/source_tables.md)
- [Silver plan](docs/silver_plan.md)
- [Silver layer](docs/silver.md)
- [Gold layer](docs/gold.md)
- [DBT layer](docs/dbt.md)
- [Dimensional marts](docs/marts.md)
- [Modeling plan](docs/modeling_plan.md)

## How to Run Locally

From the repository root, activate the Python environment and install dependencies if needed:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the Python pipeline:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
```

Run DBT DuckDB:

```powershell
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Generated data artifacts are local outputs under `data/`.

## Project Structure

```text
projects/03-retail-revenue-analytics/
|-- data/                # Local generated artifacts
|-- dbt/                 # DuckDB DBT modeling and tests
|-- docs/                # Source, layer, mart, and modeling documentation
|-- notebooks/           # Exploratory and validation notebooks
|-- src/                 # Python ingestion and processing jobs
|-- tests/               # Focused Python helper tests
`-- README.md            # Case study overview
```

## Current Limitations

- The DBT marts are local analytical contracts, not an enterprise warehouse.
- `fct_sales` is not an accounting-grade revenue ledger.
- No refund, cancellation, chargeback, settlement, tax, or revenue recognition logic is implemented.
- Order status is retained rather than silently filtering to delivered orders.
- Reviews and geolocation are documented but deferred from Silver v1 and DBT marts.
- No Spark, PostgreSQL dependency, orchestration, API, dashboard, cloud infrastructure, production SLAs, or production data contracts are claimed.

## Future Work

- Add `fact_orders` and `fact_payments` if those grains need first-class marts.
- Add `dim_order_status` or `dim_geography` after requirements and source rules are clearer.
- Add DBT docs generation or exposures if the portfolio case needs richer lineage.
- Add orchestration only after the local workflow is stable enough to benefit from it.
