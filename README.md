# Data Engineering Portfolio

Portfolio monorepo for end-to-end data engineering case studies.

This repository is organized around realistic project scenarios that show how raw data can move through ingestion, medallion-style processing, analytical serving, API access, and dashboard consumption. The current flagship case is a hospital analytics workflow that is already implemented locally through a PostgreSQL serving layer, Flask API, and React dashboard. The second case introduces job market analytics with a Bronze-first foundation and a stronger DBT-oriented modeling direction.

## Current Flagship Project

[`projects/01-hospital-analytics/`](projects/01-hospital-analytics/) is the main case study in this repository.

It demonstrates a local analytics pipeline for hospital patient-flow data, from Kaggle ingestion through medallion-style processing, PostgreSQL serving views, a Flask API, and a React dashboard.

```text
Kaggle ingestion -> Bronze profiling -> Silver processing -> Gold outputs -> PostgreSQL serving -> Flask API -> React dashboard
```

![Hospital analytics dashboard overview](projects/01-hospital-analytics/docs/assets/screenshots/dashboard-overview.png)

The screenshot above is captured from the implemented dashboard and shows the current frontend consuming the serving/API layer. For the complete case study, see the [Hospital Analytics README](projects/01-hospital-analytics/).

## What Is Implemented

- Kaggle-based raw data ingestion into a local Bronze landing area.
- Bronze inventory, profiling, and metadata generation.
- Pandas-based Silver processing for cleaned, row-level patient-flow data.
- Pandas-based Gold outputs for dashboard-ready analytical summaries.
- PostgreSQL serving tables and views over the Gold outputs.
- Flask API endpoints over the PostgreSQL serving views.
- React + Vite dashboard that consumes the Flask API.
- Layer-specific documentation for Bronze, Silver, Gold, Serving, API, and Dashboard.
- A second Bronze-first job market analytics case scaffold with Kaggle ingestion, raw profiling, exploratory notebook, and DBT modeling direction.

## Next Case Study

[`projects/02-job-market-analytics/`](projects/02-job-market-analytics/) is the next portfolio case study.

It uses the Kaggle dataset `uom190346a/ai-powered-job-market-insights` and currently focuses on the foundation layer:

```text
Kaggle ingestion -> Bronze raw landing -> Bronze profiling metadata -> future Silver/Gold/DBT modeling
```

This case intentionally does not duplicate the hospital project dashboard or API yet. Its purpose is to show a different analytical domain, job market and labor analytics, while moving the portfolio toward cleaner dimensional modeling and DBT-oriented transformation governance.

## Planned Future Iterations

- Production DBT models for transformation governance.
- PySpark or Databricks implementation once the local Spark environment is unblocked.
- Deployment, orchestration, CI/CD, and infrastructure automation.
- Authentication, authorization, and production API hardening.
- Presentation assets such as architecture diagrams and dashboard screenshots.

These items are roadmap items, not current production claims.

## Repository Structure

- [`docs/`](docs/): repository-level notes and engineering standards.
- [`shared/`](shared/): shared templates, conventions, and reusable placeholders.
- [`projects/`](projects/): individual portfolio case studies.
- [`projects/01-hospital-analytics/`](projects/01-hospital-analytics/): current end-to-end flagship project.
- [`projects/02-job-market-analytics/`](projects/02-job-market-analytics/): Bronze-first labor analytics case with DBT-oriented modeling scaffold.

## Local Python Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For notebook exploration and local validation:

```powershell
python -m pip install -r requirements-dev.txt
```

The React dashboard has its own Node/npm dependencies under [`projects/01-hospital-analytics/dashboard/`](projects/01-hospital-analytics/dashboard/). Install those separately with `npm install` from the dashboard directory.

## How the Current Case Works

The hospital analytics project uses a medallion-style local workflow:

1. Raw data is downloaded from Kaggle into the Bronze landing area.
2. Bronze jobs profile the raw CSV and write metadata without changing source values.
3. Silver processing standardizes and cleans the patient-flow records while preserving row grain.
4. Gold processing creates curated analytical CSV outputs for daily flow, referrals, and demographics.
5. The serving job loads Gold outputs into PostgreSQL and creates stable serving views.
6. A Flask API exposes those serving views over HTTP.
7. A React + Vite dashboard consumes the API for portfolio visualization.

Start with the [Hospital Analytics README](projects/01-hospital-analytics/) or the [demo/run guide](projects/01-hospital-analytics/docs/demo.md) for local execution details.
