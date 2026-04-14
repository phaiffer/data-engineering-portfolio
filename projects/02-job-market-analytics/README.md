# Job Market Analytics

Job market analytics case study using the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

## Project Objective

This project is the second portfolio case study in the monorepo. It complements the first flagship project, [`01-hospital-analytics`](../01-hospital-analytics/), by shifting the analytical domain from hospital operations to labor and job-market analytics.

The goal is to establish a clean foundation for job-market analytics: land the raw Kaggle dataset, inventory the raw files, profile the main analytical file, standardize row-preserving Silver records, produce curated Gold summaries, and add a real local DBT layer for SQL-first analytical modeling.

## Why This Case Exists

The hospital analytics project already demonstrates an end-to-end path through ingestion, Bronze, Silver, Gold, PostgreSQL serving, Flask API, and a React dashboard.

This project is intentionally different. It is focused on:

- labor and job-market analytics;
- reusable dimensional thinking;
- stronger SQL and DBT modeling;
- clear raw-to-modeled boundaries;
- an honest Bronze-first implementation that can evolve into curated analytical marts.

It does not build another dashboard or API yet.

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
-> DBT staging, intermediate, and mart models over Silver
-> Future serving or dashboard layer, if useful
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
- DBT staging, intermediate, and mart models;
- lightweight DBT source, model, and singular tests;
- lightweight exploratory notebook;
- documentation for the current Bronze, Silver, and Gold scopes.

Not implemented yet:

- PostgreSQL serving;
- Flask API;
- React dashboard;
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

Run the DBT analytical modeling layer:

```powershell
cd projects/02-job-market-analytics/dbt
dbt debug --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
```

DBT was verified with Python 3.12 and `dbt-duckdb`. If your active virtualenv uses Python 3.14 and DBT fails during import, run these commands from a Python 3.12 or 3.13 environment.

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

Raw data files and generated downstream data artifacts are local-only and ignored by Git.

## Project Structure

- [`data/`](data/): local medallion-aligned storage for Bronze, Silver, and Gold artifacts.
- [`src/`](src/): ingestion, processing, quality, utility, and job modules.
- [`dbt/`](dbt/): local DuckDB-backed DBT project with staging, intermediate, and mart models over Silver.
- [`docs/`](docs/): project and layer documentation.
- [`notebooks/`](notebooks/): exploratory notebook for source profiling.
- [`tests/`](tests/): unit and integration test placeholders.

## Future Iterations

- Add deeper DBT documentation, exposures, and CI after the local modeling path stabilizes.
- Add serving and visualization only after the analytical model has a stable shape.
