# Retail Revenue Analytics

Foundation for a retail and e-commerce analytics case study using the Kaggle dataset `olistbr/brazilian-ecommerce`.

This is the third portfolio case in the repository. It is intentionally limited to ingestion, raw inventory, and Bronze profiling so the project can grow toward dimensional modeling without pretending those decisions have already been made.

## Why This Case Exists

The repository already contains:

- `01-hospital-analytics`: a hospital operations analytics case.
- `02-job-market-analytics`: a job market analytics case with local medallion processing, DBT modeling, API, and dashboard layers.

This case adds a different analytical shape: retail revenue analytics. It creates a foundation for future fact and dimension modeling around orders, order items, products, customers, sellers, payments, and dates.

The current phase proves that the repository can support a batch-oriented analytical pipeline foundation for a multi-table business domain. It does not yet claim finished marts, KPIs, orchestration, serving APIs, dashboards, or cloud deployment.

## Dataset Choice

This project uses the Olist Brazilian E-Commerce Public Dataset from Kaggle:

- Kaggle handle: `olistbr/brazilian-ecommerce`
- Local raw folder name: `olist_brazilian_ecommerce`

Olist is a strong fit for this portfolio case because it has multiple related CSV files instead of one flat toy table. The dataset supports future modeling work around retail events and entities, including orders, order items, payments, customers, sellers, products, reviews, geolocation, and timestamps.

That structure makes it suitable for later dimensional modeling toward outputs such as `fact_sales`, `dim_product`, `dim_customer`, `dim_seller`, and `dim_date`. Those outputs are not implemented in this foundation phase.

## Current Architecture Flow

```text
Kaggle dataset
-> Bronze raw landing
-> Bronze raw file inventory
-> Bronze first-pass profiling of the largest supported CSV
-> JSON metadata artifact
```

Bronze stays raw. It does not rename columns, cast business types, deduplicate, filter, aggregate, create business keys, or define analytical fact/dimension semantics.

## Future Architecture Direction

Planned future growth can move in this direction after the raw sources are inspected:

```text
Bronze raw files
-> Silver standardized source-aligned tables
-> Dimensional modeling decisions
-> Gold revenue KPI marts
-> DBT marts
-> Orchestration
```

Likely future modeling topics include:

- order and order item grain analysis;
- customer, product, seller, and date dimensions;
- revenue, freight, payment, and order lifecycle KPIs;
- source freshness and data quality checks;
- DBT marts after stable Silver contracts exist;
- orchestration after the local batch workflow is stable.

## Implemented Now

- Kaggle ingestion through `kagglehub`.
- Local raw landing under `data/bronze/raw/olist_brazilian_ecommerce/`.
- Recursive inventory of all raw landed files, including hidden Kaggle operational artifacts.
- CSV-only eligibility for Bronze profiling.
- Main CSV selection by largest file size with deterministic path tie-break.
- Lightweight Pandas profiling of the selected CSV.
- Readable Bronze metadata JSON under `data/bronze/metadata/`.
- Exploratory notebook that reuses `src/` helpers.

## Not Implemented Yet

- Silver cleaned or standardized tables.
- Fact tables or dimension tables.
- Gold KPI marts.
- DBT project or DBT models.
- Orchestration.
- Spark.
- API.
- Dashboard.
- Cloud infrastructure.
- Production data contracts or SLAs.

## How to Run Locally

From the repository root, activate the Python environment and install the repository dependencies if needed:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run ingestion:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
```

Run Bronze inventory and profiling:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
```

Generated data artifacts are local-only and should be recreated by running the jobs.

## Project Structure

```text
projects/03-retail-revenue-analytics/
|-- data/                # Local medallion-aligned data area
|-- docs/                # Layer documentation and project notes
|-- notebooks/           # Exploratory profiling notebook
|-- src/                 # Ingestion, Bronze processing, and job entrypoints
|-- tests/               # Future validation surface
`-- README.md            # Case study overview
```

## Current Status

This project is in the foundation phase. The implemented code is useful for landing and inspecting the Olist raw dataset, but it intentionally stops before analytical modeling.

The largest-CSV profiling rule is a raw-stage convenience for first-pass inspection. It is not a final business-grain decision and should not be interpreted as choosing the final sales fact table.

## Future Iterations

- Add source-specific raw table notes after inspecting all Olist CSV files.
- Define Silver table contracts that preserve the source relationships clearly.
- Decide the sales fact grain based on orders, order items, payments, and timestamps.
- Add dimensions for product, customer, seller, geography, and date after the grain is documented.
- Add Gold revenue KPI marts only after Silver and dimensional contracts are stable.
- Add DBT and orchestration only when they have a clear role in the case study.
