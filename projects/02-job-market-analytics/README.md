# Job Market Analytics

Bronze-first job market analytics case study using the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

## Project Objective

This project is the second portfolio case study in the monorepo. It complements the first flagship project, [`01-hospital-analytics`](../01-hospital-analytics/), by shifting the analytical domain from hospital operations to labor and job-market analytics.

The goal of this first implementation step is to establish a clean foundation: land the raw Kaggle dataset, inventory the raw files, profile the main analytical file, document the source shape, and prepare the project for future Silver, Gold, and DBT-oriented analytical modeling.

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
- lightweight exploratory notebook;
- DBT scaffold notes and placeholder model files;
- documentation for the current Bronze scope.

Not implemented yet:

- Silver transformations;
- Gold marts;
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

The Bronze metadata artifact is written under:

```text
projects/02-job-market-analytics/data/bronze/metadata/
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

- Define Silver rules for field naming, data types, null handling, and categorical normalization.
- Build Gold outputs around job roles, industries, company sizes, automation exposure, salary ranges, and location-level reporting if supported by the source columns.
- Promote the DBT scaffold into real staging, intermediate, and mart models once the Silver and Gold contracts are clear.
- Add serving and visualization only after the analytical model has a stable shape.
