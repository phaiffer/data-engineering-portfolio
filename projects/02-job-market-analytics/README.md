# Job Market Analytics

Local-first job market analytics case study using the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

This is portfolio project 02. It is the SQL/dbt bridge case between the end-to-end serving story in project 01 and the richer dimensional analytics-engineering story in project 03. The architecture stays intentionally local: Python medallion processing, dbt modeling in DuckDB and PostgreSQL, PostgreSQL marts, a read-only Flask API, and a React dashboard over the modeled outputs.

## What To Review First

For a fast review, start with these files:

1. `README.md`: positioning, architecture, validation path, and local commands.
2. `dbt/models/marts/`: final SQL marts by job title, industry, location, and automation/AI adoption.
3. `dbt/models/intermediate/int_job_market_enriched.sql`: reusable row-level modeling flags.
4. `dbt/models/*/*.yml`: dbt descriptions and model tests.
5. `docs/dbt_path_comparison.md`: concise comparison of the DuckDB and PostgreSQL dbt paths.
6. `docs/local_validation.md`: lightweight validation checklist for dbt, PostgreSQL, API, and dashboard.
7. `api/routes.py` and `dashboard/src/features/Dashboard.tsx`: read layer over the PostgreSQL marts.

## Evaluate In 5 Minutes

From the repository root on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt

python projects/02-job-market-analytics/src/jobs/run_silver.py
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
```

If PostgreSQL is available and `projects/02-job-market-analytics/.env` is configured:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
.\projects\02-job-market-analytics\scripts\start_api.ps1
```

In a second terminal:

```powershell
.\projects\02-job-market-analytics\scripts\start_dashboard.ps1
```

Then open:

```text
http://127.0.0.1:5001/health
http://localhost:5173
```

## Project Overview

`02-job-market-analytics` analyzes AI-era job market signals such as job titles, industries, locations, salary ranges, automation risk, AI adoption, and growth projection.

The implementation moves one raw Kaggle dataset through:

- Bronze raw landing and profiling.
- Silver standardized, row-preserving records.
- Gold analytical summaries generated in Python.
- dbt marts modeled through both DuckDB and PostgreSQL paths.
- PostgreSQL Silver and mart tables for local relational inspection.
- A read-only Flask API.
- A React dashboard connected to the API.

The case is intentionally portfolio-oriented. It demonstrates practical local analytics engineering without claiming production deployment, orchestration, CI/CD, authentication, SLAs, or cloud hardening.

## Why This Case Exists

Project 01, [`01-hospital-analytics`](../01-hospital-analytics/), proves a complete operational analytics serving path with PostgreSQL views, a Flask API, and a React dashboard.

Project 02 is different:

- It shifts the domain from hospital operations to labor-market analytics.
- It makes SQL/dbt modeling more visible than project 01.
- It keeps Python medallion artifacts while adding dbt marts as reviewable SQL assets.
- It proves the same modeled data can run in a fast file-based DuckDB path and a PostgreSQL serving path.
- It keeps the API/dashboard thin so reviewers can focus on the modeling layer.

Project 03 is more dimensional-model-heavy. Project 02 should be read as the bridge: stronger modeling than project 01, less warehouse-first than project 03, and more analytical-modeling-focused than a simple raw-to-dashboard demo.

## Architecture Flow

```text
Kaggle dataset
-> Bronze raw landing and profiling
-> Silver standardized job-market records
-> Gold analytical summaries
-> dbt path A: DuckDB marts over Silver CSV
-> dbt path B: PostgreSQL marts over loaded Silver data
-> Flask read-only API
-> React dashboard
```

## Dashboard Preview

![Job market analytics dashboard overview](docs/assets/dashboard-overview.png)

The dashboard is not a mockup. It reads from the Flask API, which reads from PostgreSQL Silver data and dbt marts.

## Implemented Stack

- **Python**: ingestion, Bronze profiling, Silver standardization, Gold summaries, PostgreSQL loading.
- **Pandas**: local medallion transformations and profiling.
- **DuckDB**: file-based dbt development over the Silver CSV artifact.
- **PostgreSQL**: relational Silver load and dbt mart materialization.
- **dbt**: staging, intermediate, mart models, sources, model tests, and singular tests.
- **Flask**: thin read-only API for dashboard access.
- **React + Vite + TypeScript**: dashboard frontend over the API.
- **PowerShell helper scripts**: Windows-native local validation and startup commands.

## Modeling Paths

This project keeps two dbt paths on purpose. They share the same dbt model tree but use different runtimes.

| Path | Source | Output | What it proves | When to inspect |
| --- | --- | --- | --- | --- |
| DuckDB | `data/silver/ai_job_market_insights_silver.csv` | `data/job_market_analytics.duckdb` | The dbt models can run quickly against a local file artifact without PostgreSQL. | First review, SQL model review, quick local validation. |
| PostgreSQL | `analytics.job_market_insights_silver` | `marts.*` tables | The same modeling logic can materialize relational marts for the API and dashboard. | Serving-path review, API validation, database inspection. |

### Path A: DuckDB Local Modeling

```text
Silver CSV -> dbt DuckDB source -> staging -> intermediate -> marts -> local DuckDB database
```

Run from the repository root:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
```

Or run the lower-level dbt commands from the dbt directory:

```powershell
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

Main artifact:

```text
projects/02-job-market-analytics/data/job_market_analytics.duckdb
```

### Path B: PostgreSQL-Backed Modeling

```text
Silver CSV -> analytics.job_market_insights_silver -> dbt PostgreSQL source -> staging -> intermediate -> marts
```

Run from the repository root after configuring `projects/02-job-market-analytics/.env`:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

Or run the lower-level commands manually:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

PostgreSQL outputs:

```text
analytics.job_market_insights_silver
marts.mart_job_title_summary
marts.mart_industry_summary
marts.mart_location_summary
marts.mart_automation_ai_summary
```

## Key Modeling Insights

- Silver is row-preserving. It standardizes names, types, salary fields, categorical values, and metadata without changing the dataset grain.
- dbt staging keeps the Silver contract close to the source and prepares fields for SQL modeling.
- dbt intermediate modeling adds reusable flags such as remote-friendly, high automation risk, high AI adoption, and growth projection.
- dbt marts expose clear analytical grains: job title, industry, location, and automation/AI adoption combinations.
- Singular dbt tests check portfolio-relevant assumptions such as positive mart counts, valid share ranges, and salary ranges.
- Python Gold and dbt marts are parallel local analytics artifacts. The dbt marts are the stronger SQL review surface.

## Validation Surface

Use [docs/local_validation.md](docs/local_validation.md) for the full checklist.

DuckDB dbt validation:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
```

PostgreSQL load and dbt validation:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

Inspect PostgreSQL marts:

```sql
select count(*) from analytics.job_market_insights_silver;
select count(*) from marts.mart_job_title_summary;
select count(*) from marts.mart_industry_summary;
select count(*) from marts.mart_location_summary;
select count(*) from marts.mart_automation_ai_summary;
```

API health and endpoint checks:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/health
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/job-titles?limit=5&order_by=average_salary_usd&direction=desc"
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/industries?limit=5"
```

Dashboard startup:

```powershell
.\projects\02-job-market-analytics\scripts\start_dashboard.ps1
```

## Local API Examples

Start the API:

```powershell
.\projects\02-job-market-analytics\scripts\start_api.ps1
```

Primary endpoints:

```text
GET /health
GET /api/v1/kpis
GET /api/v1/job-titles
GET /api/v1/industries
GET /api/v1/locations
GET /api/v1/automation-ai
```

Example PowerShell calls:

```powershell
Invoke-RestMethod http://127.0.0.1:5001/api/v1/kpis
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/locations?limit=10&order_by=average_salary_usd&direction=desc"
Invoke-RestMethod "http://127.0.0.1:5001/api/v1/automation-ai?order_by=total_records&direction=desc"
```

The API is a read layer only. It does not rebuild Bronze, Silver, Gold, or dbt transformation logic.

## How to Run Locally

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the Python medallion pipeline:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
python projects/02-job-market-analytics/src/jobs/run_silver.py
python projects/02-job-market-analytics/src/jobs/run_gold.py
```

Run the dbt paths:

```powershell
.\projects\02-job-market-analytics\scripts\validate_dbt_duckdb.ps1
.\projects\02-job-market-analytics\scripts\validate_dbt_postgres.ps1
```

Start the API and dashboard in separate terminals:

```powershell
.\projects\02-job-market-analytics\scripts\start_api.ps1
.\projects\02-job-market-analytics\scripts\start_dashboard.ps1
```

Generated data artifacts are local-only and ignored by Git.

## Project Structure

```text
projects/02-job-market-analytics/
|-- api/                 # Read-only Flask API over PostgreSQL Silver and dbt marts
|-- dashboard/           # React + Vite dashboard consuming the API
|-- data/                # Local generated Bronze, Silver, Gold, and DuckDB artifacts
|-- dbt/                 # Shared dbt project for DuckDB and PostgreSQL targets
|-- docs/                # Layer docs, validation notes, and portfolio assets
|-- notebooks/           # Exploratory validation notebooks
|-- scripts/             # Windows PowerShell reviewer helpers
|-- src/                 # Python ingestion, processing, quality, loading, and job modules
|-- tests/               # Test placeholders and validation notes
|-- .env.example         # Local configuration template
`-- README.md            # Case study overview
```

## Known Limitations / Modeling Notes

- This is a local analytics case study, not a production deployment.
- There is no scheduler, cloud infrastructure, CI/CD pipeline, auth layer, or SLA-backed contract.
- The source dataset is a static Kaggle extract, so freshness behavior is not modeled.
- Python Gold outputs remain as local analytical summaries; dbt marts are the preferred SQL review surface.
- DuckDB is for fast local model validation. PostgreSQL is the serving path for API and dashboard reads.
- The API is intentionally thin and read-only; business logic belongs in Python transformations and dbt models.

## Current Status

Implemented:

- Kaggle ingestion into a local Bronze raw area.
- Bronze file inventory, profiling, and metadata generation.
- Silver row-preserving standardization.
- Gold analytical summaries.
- dbt DuckDB modeling over Silver CSV.
- PostgreSQL Silver loading.
- dbt PostgreSQL modeling into marts.
- dbt source, model, and singular tests.
- Read-only Flask API over PostgreSQL data.
- React dashboard consuming the real API.
- Portfolio screenshot for the dashboard.

Future iterations should stay honest about the project role: add richer dbt docs, captured validation assets, or orchestration only when those additions are implemented and useful.
