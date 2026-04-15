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

### Flask Read-Only API

The API reads from the already-modeled DuckDB marts and returns JSON responses for business-friendly endpoints such as KPIs, daily revenue, category performance, seller performance, customer-state performance, order-status summary, and payment-type summary.

The API is thin by design. It does not run DBT, rebuild marts, recalculate business logic from raw files, or write data.

### React Dashboard

The dashboard consumes the API and presents the case as a local analytics product. It includes KPI cards, daily revenue trend, category performance, seller performance, customer state performance, order status, and payment type sections.

The dashboard keeps business logic in the modeled layers and API contract. React handles API consumption, rendering, formatting, loading states, empty states, and error states.

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
- [API layer](docs/api.md)
- [Dashboard layer](docs/dashboard.md)
- [Docker packaging](docs/docker.md)
- [Modeling plan](docs/modeling_plan.md)

## How to Run

### Manual Local Path

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

Start the API from the repository root after DBT has built the DuckDB marts:

```powershell
python projects/03-retail-revenue-analytics/api/app.py
```

Default API URL:

```text
http://127.0.0.1:5002
```

The local Flask API is HTTP-only. Use `http://127.0.0.1:5002`, not `https://127.0.0.1:5002`.

Start the dashboard:

```powershell
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

The Docker path is still local-first. It improves packaging and startup ergonomics, but it does not turn the project into a production deployment.

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

## Local Connectivity Troubleshooting

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
