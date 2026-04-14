# Job Market Analytics

Job market analytics case study using the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

## Project Objective

This project is the second portfolio case study in the monorepo. It complements the first flagship project, [`01-hospital-analytics`](../01-hospital-analytics/), by shifting the analytical domain from hospital operations to labor and job-market analytics.

The goal is to establish a clean foundation for job-market analytics: land the raw Kaggle dataset, inventory the raw files, profile the main analytical file, standardize row-preserving Silver records, produce curated Gold summaries, and prepare the project for future DBT-oriented analytical modeling.

## Why This Case Exists

The hospital analytics project already demonstrates an end-to-end path through ingestion, Bronze, Silver, Gold, PostgreSQL serving, Flask API, and a React dashboard.

This project is intentionally different. It is focused on:

- labor and job-market analytics;
- reusable dimensional thinking;
- stronger SQL and DBT direction;
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
-> Future DBT models
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
- lightweight exploratory notebook;
- DBT scaffold notes and placeholder model files;
- documentation for the current Bronze, Silver, and Gold scopes.

Not implemented yet:

- production DBT models;
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

Raw data files and generated downstream data artifacts are local-only and ignored by Git.

## Project Structure

- [`data/`](data/): local medallion-aligned storage for Bronze, Silver, and Gold artifacts.
- [`src/`](src/): ingestion, processing, quality, utility, and job modules.
- [`dbt/`](dbt/): DBT scaffold for future analytical modeling.
- [`docs/`](docs/): project and layer documentation.
- [`notebooks/`](notebooks/): exploratory notebook for source profiling.
- [`tests/`](tests/): unit and integration test placeholders.

## Future Iterations

- Promote the DBT scaffold into real staging, intermediate, and mart models once the Silver and Gold contracts are clear.
- Add serving and visualization only after the analytical model has a stable shape.
