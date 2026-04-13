# Hospital Analytics

End-to-end hospital analytics portfolio case built around a local medallion-style data pipeline, PostgreSQL serving layer, Flask API, and React dashboard.

## Project Summary

This project shows how a raw hospital patient-flow dataset can be turned into analytical outputs for downstream consumption. The current implementation covers the full local path from Kaggle ingestion to dashboard visualization:

```text
Kaggle ingestion -> Bronze -> Silver -> Gold -> PostgreSQL serving -> Flask API -> React dashboard
```

The project is not presented as a production healthcare platform. It is a portfolio-grade case study focused on data engineering structure, layer separation, serving patterns, and clear documentation.

## Problem Framing

Hospital operations teams often need curated views of patient-flow activity, including daily volumes, referral patterns, demographic segments, wait time, and satisfaction indicators. Raw source files are not ideal for direct dashboard consumption because they mix ingestion concerns, raw schema quirks, and analytical logic.

This case study separates those concerns into explicit pipeline layers, then exposes curated outputs through a database-backed API and dashboard.

## Current Architecture

- **Ingestion:** downloads the Kaggle dataset into the local Bronze raw area.
- **Bronze:** inventories and profiles the raw CSV while preserving raw fidelity.
- **Silver:** standardizes column names, trims text fields, converts blanks to nulls, applies safe Pandas type casts, and writes a row-preserving cleaned dataset.
- **Gold:** creates curated analytical outputs for daily patient flow, department referrals, and demographics.
- **PostgreSQL serving:** loads Gold CSV outputs into local PostgreSQL tables and creates stable serving views.
- **Flask API:** exposes the serving views through JSON endpoints.
- **React + Vite dashboard:** consumes the Flask API and visualizes the curated analytical outputs.

Architecture diagram: to be added in [`docs/assets/`](docs/assets/).
Dashboard screenshots: to be added in [`docs/assets/`](docs/assets/).

## Medallion Layers

- **Bronze:** raw landed data plus profiling metadata. This layer documents what arrived without applying business transformations.
- **Silver:** cleaned and standardized patient-flow records at the current row grain of one patient admission or flow event.
- **Gold:** dashboard-ready aggregates and summaries built from Silver outputs.

## Implemented Stack

- Python
- Pandas
- Kaggle dataset ingestion through `kagglehub`
- PostgreSQL
- Flask
- psycopg
- React
- Vite
- TypeScript
- Recharts

## Future Stack Candidates

- PySpark or Databricks for distributed processing once the local Spark environment is unblocked.
- DBT models for transformation governance and stronger analytical modeling.
- Deployment, orchestration, CI/CD, infrastructure automation, and API hardening.

These are future iterations, not current production components.

## Folder Overview

- [`data/`](data/): local medallion-aligned data storage for Bronze, Silver, and Gold artifacts.
- [`src/`](src/): ingestion, processing, quality, serving, utility, and job modules.
- [`api/`](api/): lightweight Flask API over PostgreSQL serving views.
- [`dashboard/`](dashboard/): React + Vite dashboard over the Flask API.
- [`docs/`](docs/): layer documentation, implementation notes, and demo guide.
- [`dbt/`](dbt/): DBT scaffold and placeholder models for future transformation work.
- [`notebooks/`](notebooks/): exploratory and validation notebooks.
- [`tests/`](tests/): unit and integration test placeholders.

## Implemented Components

- [Bronze Layer](docs/bronze.md): raw file inventory, main CSV selection, profiling, and metadata output.
- [Silver Layer](docs/silver.md): row-preserving cleaned patient-flow artifact and metadata.
- [Gold Layer](docs/gold.md): curated analytical CSV outputs for dashboard-ready reporting.
- [Serving Layer](docs/serving.md): PostgreSQL tables and serving views over Gold outputs.
- [API Layer](docs/api.md): Flask endpoints for KPIs, daily patient flow, department referrals, and demographics.
- [Dashboard](dashboard/README.md): React + Vite frontend consuming the Flask API.
- [Demo / Run Guide](docs/demo.md): concise local execution flow for demos and reviewers.

## Current Status

The local end-to-end path is implemented and documented:

```text
raw Kaggle dataset -> local medallion files -> PostgreSQL serving views -> Flask JSON API -> React dashboard
```

The implementation is suitable for portfolio review and local demonstration. It remains intentionally lightweight: it does not include production orchestration, authentication, deployment infrastructure, Spark execution, or production DBT models.

## Future Iterations

- Replace or complement Pandas jobs with PySpark when the local environment supports it.
- Promote DBT placeholders into real models and tests.
- Add orchestration and CI checks for repeatable pipeline execution.
- Add deployment documentation or infrastructure only after the local case is stable.
- Add honest presentation assets such as diagrams, dashboard screenshots, and API screenshots.
- Expand test coverage around processing, serving, and API behavior.

## How to Run Locally

Use the [Demo / Run Guide](docs/demo.md) for the concise end-to-end flow.

For layer-specific details, use the [project docs index](docs/README.md). The main local flow is:

1. Activate the Python virtual environment.
2. Run or refresh Gold and PostgreSQL serving outputs as needed.
3. Start the Flask API.
4. Start the React dashboard.
5. Open the Vite local URL in the browser.

Local PostgreSQL credentials are read from `.env`; use `.env.example` as the template.
