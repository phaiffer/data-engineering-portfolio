# Job Market Analytics

Job market analytics case study using the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

## Project Objective

This project is the second portfolio case study in the monorepo. It complements the first flagship project, [`01-hospital-analytics`](../01-hospital-analytics/), by shifting the analytical domain from hospital operations to labor and job-market analytics.

The goal is to establish a clean foundation for job-market analytics: land the raw Kaggle dataset, inventory the raw files, profile the main analytical file, standardize row-preserving Silver records, produce curated Gold summaries, and add DBT modeling paths for SQL-first analytical modeling.

## Why This Case Exists

The hospital analytics project already demonstrates an end-to-end path through ingestion, Bronze, Silver, Gold, PostgreSQL serving, Flask API, and a React dashboard.

This project is intentionally different. It is focused on:

- labor and job-market analytics;
- reusable dimensional thinking;
- stronger SQL and DBT modeling;
- PostgreSQL-backed relational loading;
- clear raw-to-modeled boundaries;
- an honest Bronze-first implementation that evolves into curated analytical marts;
- a thin read-only API over the PostgreSQL mart layer for dashboard consumption.

## Dataset Focus

- Source: Kaggle
- Dataset handle: `uom190346a/ai-powered-job-market-insights`
- Current local landing path: `data/bronze/raw/ai_powered_job_market_insights/`

The Bronze job does not invent business semantics. It discovers the landed files and profiles the main CSV as raw source data.

## Planned Medallion Flow

```text
Kaggle dataset
-> Bronze raw landing and profiling
-> Silver standardized job-market records
-> Gold dimensional or mart-style analytical outputs
-> DBT path A: DuckDB staging, intermediate, and marts over the Silver CSV
-> DBT path B: PostgreSQL staging, intermediate, and marts over loaded Silver data
-> Thin read-only Flask API over PostgreSQL Silver and DBT marts
-> Dashboard-ready JSON endpoints
```

## Current Implementation Status

Implemented in this foundation step:

- project scaffold under `projects/02-job-market-analytics/`;
- Kaggle ingestion with `kagglehub`;
- local raw Bronze landing area;
- raw file inventory helpers;
- Bronze v1 profiling with Pandas;
- JSON metadata generation for the selected main CSV;
- Silver v1 row-preserving standardization with Pandas;
- Gold v1 curated analytical summaries with Pandas;
- local DBT project using DuckDB over the Silver artifact;
- PostgreSQL Silver loader for `analytics.job_market_insights_silver`;
- DBT PostgreSQL target over the loaded Silver table;
- shared DBT staging, intermediate, and mart models;
- final DBT PostgreSQL marts materialized in the `marts` schema;
- lightweight DBT source, model, and singular tests;
- thin read-only Flask API over PostgreSQL Silver and DBT marts;
- lightweight exploratory notebook;
- documentation for the current Bronze, Silver, and Gold scopes.

Not implemented yet:

- PostgreSQL serving views beyond the DBT marts;
- orchestration, deployment, or infrastructure.

## How to Run Locally

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Download the Kaggle dataset into the project-local Bronze raw area:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
```

Run the Bronze inventory and profiling job:

```powershell
python projects/02-job-market-analytics/src/jobs/run_bronze.py
```

Run the Silver standardization job:

```powershell
python projects/02-job-market-analytics/src/jobs/run_silver.py
```

Run the Gold summary job:

```powershell
python projects/02-job-market-analytics/src/jobs/run_gold.py
```

Run the DBT DuckDB analytical modeling path:

```powershell
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

DBT is not meant to run from the repository base `.venv` when that environment uses an incompatible Python version. The helper scripts use `uv`, Python 3.12, and the DBT-specific dependency file at `projects/02-job-market-analytics/dbt/requirements.txt`.

To run the PostgreSQL modeling path, configure `projects/02-job-market-analytics/.env`, load Silver into PostgreSQL, and run DBT with the PostgreSQL target:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

The Bronze metadata artifact is written under:

```text
projects/02-job-market-analytics/data/bronze/metadata/
```

The Silver artifact and metadata are written under:

```text
projects/02-job-market-analytics/data/silver/
```

The Gold artifacts and metadata are written under:

```text
projects/02-job-market-analytics/data/gold/
```

The local DBT DuckDB database is written to:

```text
projects/02-job-market-analytics/data/job_market_analytics.duckdb
```

The PostgreSQL Silver load writes to:

```text
analytics.job_market_insights_silver
```

The PostgreSQL DBT analytical outputs materialize to:

```text
marts.mart_job_title_summary
marts.mart_industry_summary
marts.mart_location_summary
marts.mart_automation_ai_summary
```

Start the local read-only dashboard API:

```powershell
.\.venv\Scripts\python.exe projects/02-job-market-analytics/api/app.py
```

The API runs at `http://127.0.0.1:5001` by default and exposes:

```text
GET /health
GET /api/v1/kpis
GET /api/v1/job-titles
GET /api/v1/industries
GET /api/v1/locations
GET /api/v1/automation-ai
```

Start the first React dashboard:

```powershell
cd projects/02-job-market-analytics/dashboard
npm install
npm run dev
```

The dashboard reads from the PostgreSQL Silver table and DBT marts through the thin Flask API. It does not use the Figma mock numbers or rebuild any medallion-layer logic in the frontend.

Raw data files and generated downstream data artifacts are local-only and ignored by Git.

## Project Structure

- [`data/`](data/): local medallion-aligned storage for Bronze, Silver, and Gold artifacts.
- [`src/`](src/): ingestion, processing, quality, utility, and job modules.
- [`dbt/`](dbt/): DBT project with DuckDB and PostgreSQL targets sharing staging, intermediate, and mart models over Silver.
- [`api/`](api/): thin read-only Flask API for dashboard access to PostgreSQL Silver and DBT marts.
- [`dashboard/`](dashboard/): React, Vite, and TypeScript dashboard over the modeled outputs.
- [`docs/`](docs/): project, layer, and API documentation.
- [`notebooks/`](notebooks/): exploratory notebook for source profiling.
- [`tests/`](tests/): unit and integration test placeholders.

## Future Iterations

- Add deeper DBT documentation, exposures, and CI after the local modeling path stabilizes.
- Add serving and visualization only after the analytical model has a stable shape.
