# Retail Revenue Analytics

Retail and e-commerce analytics case study using the Kaggle dataset `olistbr/brazilian-ecommerce`.

This is the third portfolio case in the repository. It now implements a local Bronze, source-aligned Silver, and cautious Gold v1 layer for revenue and business KPI summaries. Dimensional modeling, DBT, orchestration, API, dashboard, cloud deployment, and production contracts remain future work.

## Why This Case Exists

The repository already contains:

- `01-hospital-analytics`: a hospital operations analytics case with serving-oriented outputs.
- `02-job-market-analytics`: a job market analytics case with Python processing, DBT marts, API, and dashboard layers.

This third case adds a different analytical shape: retail revenue analytics over a multi-table marketplace dataset.

The project is meant to prove:

- source-aware Silver design;
- dimensional modeling readiness;
- fact and dimension thinking without prematurely creating final marts;
- careful revenue KPI definitions;
- batch-oriented analytical pipeline foundations;
- a clean path toward future DBT marts and orchestration.

## Dataset Choice

This project uses the Olist Brazilian E-Commerce Public Dataset from Kaggle:

- Kaggle handle: `olistbr/brazilian-ecommerce`
- Local raw folder name: `olist_brazilian_ecommerce`

Olist is a strong fit because it has multiple related CSV files instead of one flat sales table. The landed dataset includes orders, order items, payments, products, category translations, customers, sellers, reviews, and geolocation.

That structure supports future modeling around facts such as order items, orders, and payments, plus dimensions such as product, customer, seller, date, order status, and geography.

## Current Architecture Flow

```text
Kaggle dataset
-> Bronze raw landing and profiling
-> Silver source-aligned standardized tables
-> Gold revenue KPI summaries
-> future dimensional modeling / DBT marts / orchestration
```

The current project is local-first and inspectable. It does not claim production maturity.

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

Silver preserves each source table grain. It applies only safe standardization: column-name normalization, whitespace trimming, blank-string null handling, and configured datetime/numeric parsing.

Silver does not aggregate, deduplicate, create surrogate keys, or join everything into one canonical table.

### Gold v1

Gold v1 produces first-pass analytical outputs:

```text
kpi_overview.csv
daily_revenue_summary.csv
category_revenue_summary.csv
seller_revenue_summary.csv
customer_state_revenue_summary.csv
payment_type_summary.csv
order_status_summary.csv
```

Revenue measures are item-side:

- `item_revenue = sum(order_items.price)`
- `freight_value = sum(order_items.freight_value)`
- `gross_merchandise_value = sum(order_items.price + order_items.freight_value)`

Payments are summarized separately by payment type and are not joined to order items for revenue totals. This avoids double counting when an order has multiple payment rows.

## Documentation

- [Bronze layer](docs/bronze.md)
- [Source tables](docs/source_tables.md)
- [Silver plan](docs/silver_plan.md)
- [Silver layer](docs/silver.md)
- [Modeling plan](docs/modeling_plan.md)
- [Gold layer](docs/gold.md)

## How to Run Locally

From the repository root, activate the Python environment and install dependencies if needed:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the local pipeline:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
```

Generated data artifacts are local outputs under `data/`.

## Project Structure

```text
projects/03-retail-revenue-analytics/
|-- data/                # Local Bronze, Silver, and Gold artifacts
|-- docs/                # Source, layer, and modeling documentation
|-- notebooks/           # Exploratory and validation notebooks
|-- src/                 # Ingestion and processing jobs
|-- tests/               # Focused helper tests
`-- README.md            # Case study overview
```

## Current Limitations

- Gold v1 is not a finished accounting model.
- Gold v1 is not a final dimensional mart design.
- No refund, cancellation, chargeback, or settlement reconciliation is implemented.
- Order status is retained rather than silently filtering to delivered orders.
- Reviews and geolocation are documented but deferred from Silver v1.
- DBT is not implemented yet.
- No Spark, orchestration, API, dashboard, cloud infrastructure, production SLAs, or production data contracts are claimed.

## Future Dimensional Modeling Direction

Likely future facts:

- `fact_order_items`: primary item-side revenue fact.
- `fact_orders`: order lifecycle and status fact.
- `fact_payments`: payment behavior fact.

Likely future dimensions:

- `dim_product`
- `dim_customer`
- `dim_seller`
- `dim_date`
- `dim_order_status`
- `dim_geography` after geolocation rules are defined

Future DBT marts should be added only after the Silver contracts and dimensional grain decisions are stable enough to justify them.
