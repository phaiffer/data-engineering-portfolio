# Retail Revenue Analytics

Retail and e-commerce analytics case study using the Kaggle dataset `olistbr/brazilian-ecommerce`.

This is the third portfolio case in the repository. It implements a local Bronze layer, source-aligned Silver tables, cautious Python Gold v1 KPI summaries, DBT DuckDB dimensional marts, and a thin read-only Flask API over those marts. The project remains local-first and portfolio-oriented, with no production maturity claims.

## Why This Case Exists

The repository already contains:

- `01-hospital-analytics`: a hospital operations analytics case with serving-oriented outputs.
- `02-job-market-analytics`: a job market analytics case with Python processing, DBT marts, API, and dashboard layers.

This third case adds a retail marketplace domain with stronger dimensional modeling emphasis. It shows how a multi-table source can move from raw files to source-aligned Silver tables, then into fact, dimension, mart-style SQL models, a read-only API, and a local dashboard.

The project proves:

- source-aware Silver design;
- careful order, item, payment, product, customer, and seller relationships;
- item-grain sales modeling;
- payment duplication avoidance;
- DBT as a local modeling and testing layer;
- a thin analytical serving contract over modeled marts;
- a React presentation layer over the analytical API;
- a cleaner Docker packaging path for local demos and reproducibility;
- a clean path toward future orchestration without adding it prematurely.

## Business Problem

Retail leaders need a reliable way to understand revenue performance across products, categories, sellers, customer regions, order status, and payment behavior. The raw Olist export is spread across orders, items, products, customers, sellers, and payments, so direct reporting can easily double-count revenue or mix grains.

This project turns those source tables into a batch-built analytical model that answers business questions such as:

- Which product categories generate the most item-side revenue?
- Which sellers or seller states drive the strongest marketplace performance?
- How does daily revenue change by order status?
- Which customer states contribute the most orders and revenue?
- Which payment methods are most common, and how large are their payment values?
- How many order-item rows, orders, and item-side sales dollars are represented in the model?

## Business Value

The model helps a retail analytics team prioritize category investment, review seller performance, monitor order-status impact on revenue, understand regional demand, and separate product-sales metrics from payment behavior. It is intentionally shaped as a portfolio case study for dimensional modeling and KPI design rather than as an accounting ledger.

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
-> Flask read-only API
-> React dashboard
```

```mermaid
flowchart LR
    raw["Raw Olist CSV files"] --> bronze["Bronze raw landing and profiling"]
    bronze --> silver["Silver source-aligned tables"]
    silver --> modeled["Dimensions and facts in dbt"]
    modeled --> gold["Gold reporting marts"]
    gold --> api["Read-only Flask API"]
    api --> dashboard["React dashboard"]
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
- `dim_store`
- `dim_salesperson`
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

### Flask Read-Only API

The API reads from the already-modeled DuckDB marts and returns JSON responses for business-friendly endpoints such as KPIs, daily revenue, category performance, seller performance, customer-state performance, order-status summary, and payment-type summary.

The API is thin by design. It does not run DBT, rebuild marts, recalculate business logic from raw files, or write data.

### React Dashboard

The dashboard consumes the API and presents the case as a local analytics product. It includes KPI cards, daily revenue trend, category performance, seller performance, customer state performance, order status, and payment type sections.

The dashboard keeps business logic in the modeled layers and API contract. React handles API consumption, rendering, formatting, loading states, empty states, and error states.

## Revenue And Grain Rules

The central analytical fact is `fct_sales`, which represents the conceptual `fact_sales` model for this portfolio case.

Fact grain: one row per sold item per order, identified by `order_id` and `order_item_id`.

Core dimensional model:

- `fact_sales` / implemented as `fct_sales`: one order-item row with item-side revenue measures and order-level payment context.
- `dim_date`: purchase-date calendar attributes.
- `dim_product`: product and category attributes.
- `dim_customer`: customer identity and coarse geography.
- `dim_store`: seller storefront proxy because Olist does not provide physical stores.
- `dim_salesperson`: seller proxy because Olist does not provide named salespeople.
- `dim_seller`: retained source-aligned marketplace seller dimension used by existing marts and dashboard endpoints.

Item-side measures:

- `item_price = order_items.price`
- `freight_value = order_items.freight_value`
- `gross_merchandise_value = item_price + freight_value`

Raw payment rows are not joined directly to item rows. DBT aggregates payments to one row per order before adding payment context to `fct_sales`.

Payment fields in `fct_sales` are order-level context. They can repeat across multi-item orders and should not be summed as item-level sales revenue.

## KPI Definitions

Primary KPIs are documented in [KPI definitions](docs/kpis.md). The core implemented metrics are:

- `gross_revenue`: `sum(item_price + freight_value)`.
- `net_revenue`: `sum(item_price)`.
- `units_sold`: `count(*)` at `fct_sales` grain.
- `order_count`: `count(distinct order_id)`.
- `average_order_value`: `sum(item_price) / count(distinct order_id)`.

Discount, margin, and profit metrics are documented as future-ready definitions, but they are not calculated because the selected Olist source tables do not contain discount, product cost, fee, tax, or settlement inputs.

## Batch Load Strategy

This project uses full-batch local rebuilds. Silver and Gold outputs are overwritten on each run, and dbt rebuilds DuckDB marts from the current Silver tables. That makes reruns safe for the same raw inputs and keeps the portfolio workflow easy to inspect.

The next incremental step would be partitioned processing by `order_purchase_date` with a lookback window for late-arriving order items, payment records, or status changes. Current duplicate protection is expressed through source-grain and fact-grain tests instead of hidden append logic.

## Data Quality Checks

Data quality is handled with dbt tests and lightweight Python run metadata. Current checks validate:

- no nulls in critical keys;
- uniqueness where dimensions or source grains require it;
- referential integrity between `fct_sales` and dimensions;
- no duplicate fact rows at `order_id` and `order_item_id` grain;
- non-negative sales and payment values;
- valid purchase dates;
- order-level payment aggregation before joining to item-grain facts.

See [Data quality and rerun safety](docs/data_quality.md) for the validation and observability details.

## Design Trade-offs

Batch instead of streaming: Olist is a static analytical export, and the business questions are periodic revenue-analysis questions. Batch processing keeps the logic reproducible and avoids unnecessary infrastructure.

Dimensional modeling: the source has multiple natural grains, so facts and dimensions make KPI definitions clearer and reduce double-counting risk, especially around payments and order items.

Bridge toward dbt marts: Python handles raw local file preparation, while dbt owns modeled analytical contracts, tests, and future mart evolution. This creates a clean path toward orchestration later without adding orchestration before it is useful.

## Documentation

- [Bronze layer](docs/bronze.md)
- [Source tables](docs/source_tables.md)
- [Silver plan](docs/silver_plan.md)
- [Silver layer](docs/silver.md)
- [Gold layer](docs/gold.md)
- [KPI definitions](docs/kpis.md)
- [Data quality and rerun safety](docs/data_quality.md)
- [DBT layer](docs/dbt.md)
- [Dimensional marts](docs/marts.md)
- [API layer](docs/api.md)
- [Dashboard layer](docs/dashboard.md)
- [Docker packaging](docs/docker.md)
- [Modeling plan](docs/modeling_plan.md)

## How to Run

### Quick Demo

The shortest successful review path is:

1. create a local Python environment;
2. build Silver outputs and DuckDB marts;
3. start the API and dashboard demo stack.

Bronze and Gold are still implemented and documented, but they are not required for the shortest visible API and dashboard demo.

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt -r projects/03-retail-revenue-analytics/dbt/requirements.txt
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
(cd projects/03-retail-revenue-analytics/dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb)
(cd projects/03-retail-revenue-analytics && docker compose up --build retail-api retail-dashboard)
```

Open:

```text
API:       http://127.0.0.1:5002
Dashboard: http://127.0.0.1:4173
```

### Manual Local Path

From the repository root, create and activate a Python environment, then install the local Python and DBT dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r projects/03-retail-revenue-analytics/dbt/requirements.txt
```

PowerShell activation still works with:

```powershell
.\.venv\Scripts\Activate.ps1
```

If the raw Olist files are not already present under `data/bronze/raw/olist_brazilian_ecommerce`, run ingestion first. This step requires the same Kaggle credentials the rest of the repository uses:

```bash
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
```

Run Bronze:

```bash
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
```

Run Silver:

```bash
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
```

Run Gold:

```bash
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
```

Project-local Make targets are also available from `projects/03-retail-revenue-analytics`:

```bash
make silver
make gold
make dbt-run
make dbt-test
make test
make dashboard-build
```

Build and validate the DuckDB marts:

```bash
cd projects/03-retail-revenue-analytics/dbt
python -m dbt.cli.main debug --profiles-dir . --target duckdb
python -m dbt.cli.main run --profiles-dir . --target duckdb
python -m dbt.cli.main test --profiles-dir . --target duckdb
cd ../../..
```

The expected mart database path is:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

If you prefer PowerShell for DBT, the helper script is still available from `projects/03-retail-revenue-analytics/dbt`:

```powershell
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Start the API from the repository root after DBT has built the DuckDB marts:

```bash
python projects/03-retail-revenue-analytics/api/app.py
```

Default API URL:

```text
http://127.0.0.1:5002
```

The local Flask API is HTTP-only. Use `http://127.0.0.1:5002`, not `https://127.0.0.1:5002`.

In a second terminal, start the dashboard:

```bash
cd projects/03-retail-revenue-analytics/dashboard
npm install
npm run dev
```

Default dashboard URL:

```text
http://127.0.0.1:5173
```

If Vite falls back to another local port, the API allows common local Vite origins and HTTP `localhost` or `127.0.0.1` origins on ports `5173` through `5199` for local development.

### Docker-Assisted Local Path

Docker support is included for a cleaner demo path:

- `docker/api.Dockerfile` for the Flask API;
- `docker/dashboard.Dockerfile` for the dashboard static build and lightweight web server;
- `docker-compose.yml` for the local demo stack;
- `docker/pipeline.Dockerfile` for explicit Python job and DBT commands when needed.

The Docker path is still local-first. It improves packaging and startup ergonomics, but it does not turn the project into a production deployment, and it is not required for day-to-day development.

The normal Docker demo flow expects the DuckDB mart database to already exist under:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

From the project directory:

```bash
cd projects/03-retail-revenue-analytics
docker compose up --build retail-api retail-dashboard
```

Expected host URLs:

```text
API:       http://127.0.0.1:5002
Dashboard: http://127.0.0.1:4173
```

The dashboard image uses a browser-facing API URL baked into the build. By default that is:

```text
http://127.0.0.1:5002
```

That host URL is intentional. The browser needs a host-reachable API endpoint rather than a Docker-internal hostname.

### Optional Pipeline Container

The optional `retail-pipeline` service exists for explicit commands only. It does not run during the normal `docker compose up` path.

On Linux, prefer passing your host UID and GID when you run the pipeline container so bind-mounted DBT artifacts are written with your user ownership instead of `root`.

Use `HOST_UID` and `HOST_GID` in the command examples. `UID` is a readonly shell variable in `bash`, so `HOST_UID` avoids that shell-level footgun.

Examples:

```bash
cd projects/03-retail-revenue-analytics
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_bronze.py
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_silver.py
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_gold.py
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline sh -lc "cd dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb"
```

Use the same Kaggle credentials you would use locally if you want to run ingestion inside the pipeline container.

`dbt/logs/` and `dbt/target/` are generated local artifacts. They should not be treated as source files, and the Docker workflow should not rely on them being root-owned.

If an older Docker run left those folders owned by `root`, recover with:

```bash
cd projects/03-retail-revenue-analytics
sudo chown -R "$USER":"$(id -gn)" dbt/logs dbt/target
```

Or remove and recreate them:

```bash
cd projects/03-retail-revenue-analytics
sudo rm -rf dbt/logs dbt/target
mkdir -p dbt/logs dbt/target
```

## Troubleshooting

### API returns 503 or `/health` is degraded

The usual cause is a missing DuckDB mart file. The API starts, but it cannot serve mart-backed endpoints until DBT has created:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

Recover by rebuilding the DBT marts in the manual path, or by confirming the same file exists before you start the Docker demo path.

### Dashboard says the API is unavailable

The usual causes are:

- the API process or container is not running;
- `VITE_API_BASE_URL` points to the wrong host or port;
- the URL uses `https://` instead of `http://`;
- the current browser origin is not allowed by the API CORS settings.

Opening `http://127.0.0.1:5002/health` directly in a browser confirms the route is reachable, but it does not prove the dashboard can fetch it. Browser `fetch` from Vite also depends on CORS.

Wrong API base URL:

```text
https://127.0.0.1:5002
```

Right API base URL:

```text
http://127.0.0.1:5002
```

If the dashboard reports the API as unavailable, check that the Flask process is running, `VITE_API_BASE_URL` uses HTTP, and the current Vite origin is allowed by the API CORS configuration.

For the Docker-assisted path, also check that:

- `retail-api` is published on `http://127.0.0.1:5002`;
- `retail-dashboard` is published on `http://127.0.0.1:4173`;
- the DuckDB file exists under `data/retail_revenue_analytics.duckdb`;
- the dashboard image was built with a host-reachable API URL.

### DBT permission denied on Linux

The usual cause is an older container run that created `dbt/logs/` or `dbt/target/` as `root` on the bind-mounted project directory.

Recover by fixing ownership:

```bash
cd projects/03-retail-revenue-analytics
sudo chown -R "$USER":"$(id -gn)" dbt/logs dbt/target
```

If you also find a root-owned mart database, fix that file too:

```bash
sudo chown "$USER":"$(id -gn)" data/retail_revenue_analytics.duckdb
```

Or reset the generated DBT artifacts completely:

```bash
cd projects/03-retail-revenue-analytics
sudo rm -rf dbt/logs dbt/target
mkdir -p dbt/logs dbt/target
```

Generated data artifacts are local outputs under `data/`.

## Project Structure

```text
projects/03-retail-revenue-analytics/
|-- data/                # Local generated artifacts
|-- dbt/                 # DuckDB DBT modeling and tests
|-- api/                 # Thin read-only Flask API over DuckDB marts
|-- dashboard/           # React + Vite dashboard over the API
|-- docker/              # Dockerfiles and container-specific requirements
|-- docs/                # Source, layer, mart, and modeling documentation
|-- notebooks/           # Exploratory and validation notebooks
|-- src/                 # Python ingestion and processing jobs
|-- tests/               # Focused Python helper tests
|-- docker-compose.yml   # Local Docker demo stack
`-- README.md            # Case study overview
```

## Current Limitations

- The DBT marts are local analytical contracts, not an enterprise warehouse.
- `fct_sales` is not an accounting-grade revenue ledger.
- No refund, cancellation, chargeback, settlement, tax, or revenue recognition logic is implemented.
- Order status is retained rather than silently filtering to delivered orders.
- Reviews and geolocation are documented but deferred from Silver v1 and DBT marts.
- The API is local and read-only, not production hardened.
- The dashboard is a local analytical presentation layer, not a production commerce application.
- The Docker setup improves local packaging and demo ergonomics, but it is not production infrastructure.
- No Spark, PostgreSQL dependency, orchestration, cloud infrastructure, production SLAs, or production data contracts are claimed.

## Future Work

- Add `fact_orders` and `fact_payments` if those grains need first-class marts.
- Add `dim_order_status` or `dim_geography` after requirements and source rules are clearer.
- Add DBT docs generation or exposures if the portfolio case needs richer lineage.
- Add orchestration only after the local workflow is stable enough to benefit from it.
