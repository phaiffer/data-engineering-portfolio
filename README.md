# Data Engineering Portfolio

Portfolio monorepo for end-to-end data engineering case studies.

This repository is organized around realistic project scenarios that show how raw data moves through ingestion, medallion-style processing, analytical modeling, API access, and dashboard consumption. The goal is to present practical data engineering work that is easy for technical reviewers and recruiters to scan without overstating production maturity.

## Portfolio Cases

### 01. Hospital Analytics

[`projects/01-hospital-analytics/`](projects/01-hospital-analytics/) demonstrates a local analytics pipeline for hospital patient-flow data.

```text
Kaggle ingestion -> Bronze profiling -> Silver processing -> Gold outputs -> PostgreSQL serving -> Flask API -> React dashboard
```

Implemented highlights:

- Kaggle-based raw data ingestion.
- Bronze inventory and profiling.
- Pandas-based Silver and Gold processing.
- PostgreSQL serving tables and views.
- Flask API over the serving layer.
- React + Vite dashboard consuming the API.
- Layer-specific documentation for Bronze, Silver, Gold, Serving, API, and Dashboard.

![Hospital analytics dashboard overview](projects/01-hospital-analytics/docs/assets/screenshots/dashboard-overview.png)

See the [Hospital Analytics README](projects/01-hospital-analytics/) for the complete case study.

### 02. Job Market Analytics

[`projects/02-job-market-analytics/`](projects/02-job-market-analytics/) is the second end-to-end portfolio case. It analyzes AI-era job market data using a Python medallion pipeline, dual DBT modeling paths, PostgreSQL marts, a read-only API, and a React dashboard.

```text
Kaggle dataset -> Bronze profiling -> Silver records -> Gold summaries -> DBT DuckDB marts + DBT PostgreSQL marts -> Flask API -> React dashboard
```

Implemented highlights:

- Python Bronze, Silver, and Gold pipeline over the Kaggle job-market dataset.
- DBT path A using DuckDB over the Silver CSV artifact.
- DBT path B using PostgreSQL over the loaded Silver table.
- PostgreSQL marts for job titles, industries, locations, and automation/AI summaries.
- Thin read-only Flask API over PostgreSQL Silver data and DBT marts.
- React + Vite dashboard consuming the real API.
- Curated documentation and dashboard screenshot for portfolio review.

![Job market analytics dashboard overview](projects/02-job-market-analytics/docs/assets/dashboard-overview.png)

See the [Job Market Analytics README](projects/02-job-market-analytics/) for architecture, local run instructions, and current implementation status.

## Repository Structure

- [`docs/`](docs/): repository-level notes and engineering standards.
- [`shared/`](shared/): shared templates, conventions, and reusable placeholders.
- [`projects/`](projects/): individual portfolio case studies.
- [`projects/01-hospital-analytics/`](projects/01-hospital-analytics/): hospital patient-flow analytics case.
- [`projects/02-job-market-analytics/`](projects/02-job-market-analytics/): job-market analytics case with Python, DBT, PostgreSQL, API, and dashboard layers.

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

Each React dashboard has its own Node/npm dependencies under the project-specific `dashboard/` directory. Install those separately with `npm install` from the relevant dashboard folder.

## Roadmap

Future work across the portfolio may include:

- Orchestration once the local workflows are stable enough to justify it.
- CI/CD and automated validation.
- Deployment and infrastructure notes after real deployed environments exist.
- Authentication, authorization, and API hardening where appropriate.
- Additional presentation assets such as architecture diagrams and validation screenshots.

These are roadmap items, not current production claims.
