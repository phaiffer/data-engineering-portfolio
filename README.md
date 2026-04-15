# Data Engineering Portfolio

`phaiffer/data-engineering-portfolio` is a repository of three local-first analytics case studies:

- [`projects/01-hospital-analytics/`](projects/01-hospital-analytics/)
- [`projects/02-job-market-analytics/`](projects/02-job-market-analytics/)
- [`projects/03-retail-revenue-analytics/`](projects/03-retail-revenue-analytics/)

Together they show a progression from end-to-end local analytics delivery to stronger SQL and DBT modeling, and then to the clearest dimensional-modeling and analytics-serving case in the portfolio.

In under two minutes, a reviewer should be able to see:

- what this repository is;
- what each case proves;
- how the cases differ;
- why project 03 is the strongest dimensional-modeling example;
- how to run the work locally;
- what is implemented today versus what remains roadmap.

## Why This Portfolio Exists

This portfolio exists to show practical data engineering work in a format that is easy to inspect locally.

The goal is not to present a production platform. The goal is to show how raw datasets can move through clear analytical layers, become queryable outputs, and end up in small but real API and dashboard surfaces.

Across the repository, the recurring themes are:

- medallion-style data processing;
- clear boundaries between raw, standardized, and analytical layers;
- lightweight serving patterns;
- recruiter-friendly presentation without inflating maturity claims.

## Portfolio Case Studies Overview

### 01. Hospital Analytics

[`projects/01-hospital-analytics/`](projects/01-hospital-analytics/) is the foundation case.

It proves a full local analytics product flow:

- ingestion from a Kaggle source;
- Bronze, Silver, and Gold processing;
- PostgreSQL serving tables and views;
- Flask API endpoints;
- React dashboard consumption.

This is the case that shows the repository can deliver a complete analytics path from raw data to a reviewable frontend.

### 02. Job Market Analytics

[`projects/02-job-market-analytics/`](projects/02-job-market-analytics/) extends the portfolio into a stronger SQL and DBT workflow.

It proves:

- Python medallion processing;
- DBT DuckDB and DBT PostgreSQL modeling paths;
- relational marts;
- read-only API patterns;
- dashboard delivery over modeled outputs.

This is the case that makes the SQL and DBT layer materially stronger than project 01.

### 03. Retail Revenue Analytics

[`projects/03-retail-revenue-analytics/`](projects/03-retail-revenue-analytics/) is the strongest analytics engineering case in the repository today.

It proves:

- multi-table retail source handling;
- Bronze profiling over a more realistic dataset shape;
- source-aligned Silver tables;
- Gold KPI summaries;
- DBT DuckDB dimensional marts;
- fact and dimension modeling;
- read-only API access over marts;
- dashboard consumption over the API.

This is the clearest dimensional-modeling and analytics-serving example in the portfolio.

## Case-by-Case Breakdown

### Project 01 - Hospital Analytics

**Domain:** hospital patient flow and operational reporting.

**What it proves today:**

- local ingestion and medallion processing;
- row-preserving standardization in Silver;
- dashboard-oriented Gold outputs;
- PostgreSQL as a serving layer;
- Flask API plus React dashboard as a complete local review surface.

**How it is positioned in the portfolio:**

This is the best "end-to-end analytics product flow" example. It is less SQL-modeling-heavy than projects 02 and 03, but it is the clearest proof that the repository can move from raw data to a working dashboard-backed experience.

### Project 02 - Job Market Analytics

**Domain:** labor-market and AI-impact analytics.

**What it proves today:**

- Python Bronze, Silver, and Gold processing;
- DBT DuckDB marts over the Silver artifact;
- DBT PostgreSQL marts over loaded Silver data;
- a stronger SQL modeling layer than project 01;
- read-only API and dashboard patterns over modeled outputs.

**How it is positioned in the portfolio:**

This is the bridge case between a pipeline-first implementation and a more analytics-engineering-oriented modeling layer. It is stronger than project 01 in SQL and DBT depth, but it is still more mart-oriented than full dimensional modeling.

### Project 03 - Retail Revenue Analytics

**Domain:** retail and e-commerce revenue analytics using the Olist dataset.

**Why the source matters:**

Olist is a stronger modeling dataset than a single flat file because it lands as multiple related tables such as orders, order items, payments, products, customers, and sellers. That makes it a better portfolio case for source-aware Silver design, careful joins, and mart-building discipline.

**What it proves today:**

- Bronze profiling across a multi-table retail source;
- source-aligned Silver tables rather than an early all-in-one flattening step;
- Python Gold KPI summaries for first-pass business review;
- DBT DuckDB staging, intermediate, and mart layers;
- a fact-like sales table plus supporting dimensions;
- read-only Flask API endpoints over the modeled marts;
- a React dashboard consuming the API.

**Why it is the strongest dimensional-modeling case:**

Project 03 includes `fct_sales` plus supporting dimensions such as `dim_product`, `dim_customer`, `dim_seller`, and `dim_date`, along with business-facing marts. That makes it the strongest dimensional-modeling and analytics-serving case in the repository today.

**Important modeling caveats:**

- Revenue measures are analytical item-side measures, not accounting-grade revenue.
- Payment summaries are behavior-oriented and modeled separately from item-side sales measures.
- Raw payment rows are aggregated to order grain before being added as context, which helps avoid naive duplication when orders have multiple payment rows.
- The marts are credible local analytical contracts, not an overclaimed enterprise warehouse.

## Comparison / Capability Matrix

| Case | Domain | Ingestion | Bronze | Silver | Gold | DBT | Warehouse / DB | API | Dashboard | Dimensional Modeling |
|------|--------|-----------|--------|--------|------|-----|----------------|-----|-----------|----------------------|
| [`01-hospital-analytics`](projects/01-hospital-analytics/) | Hospital operations | Kaggle to local raw files | Yes | Yes | Yes | Scaffold only | PostgreSQL serving layer | Flask | React | Limited; not the primary focus |
| [`02-job-market-analytics`](projects/02-job-market-analytics/) | Job market / AI impact | Kaggle to local raw files | Yes | Yes | Yes | Yes: DuckDB + PostgreSQL marts | DuckDB + PostgreSQL | Read-only Flask | React | Moderate; stronger marts than 01 |
| [`03-retail-revenue-analytics`](projects/03-retail-revenue-analytics/) | Retail / e-commerce | Kaggle Olist multi-table source | Yes | Yes: source-aligned tables | Yes | Yes: DuckDB staging, intermediate, and marts | DuckDB | Read-only Flask | React | Strongest; fact + dimensions |

## Repository Structure

```text
data-engineering-portfolio/
|-- projects/
|   |-- 01-hospital-analytics/
|   |-- 02-job-market-analytics/
|   `-- 03-retail-revenue-analytics/
|-- docs/
|-- shared/
|-- requirements.txt
`-- requirements-dev.txt
```

- `projects/` contains the portfolio case studies.
- `docs/` contains repository-level notes.
- `shared/` contains shared templates, conventions, and reusable repository assets.
- `requirements.txt` contains the root Python dependencies used across the local portfolio setup.

## Local Setup

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Optional notebook and validation extras:

```powershell
python -m pip install -r requirements-dev.txt
```

Each dashboard has its own frontend dependencies. Run `npm install` inside the relevant `dashboard/` directory before `npm run dev`.

## Project-Specific Run Notes

- **Project 01** uses PostgreSQL as the serving database for the API and dashboard path.
- **Project 02** supports two DBT paths: DuckDB for local modeling and PostgreSQL for the served mart and API path.
- **Project 03** is DuckDB-first for its current modeled marts and does not require PostgreSQL for the implemented API and dashboard path.
- **Projects 01 and 02** read local PostgreSQL settings from project-level `.env` files; start from each project's `.env.example`.
- **All dashboards** include a `dashboard/.env.example` with the expected local API base URL.
- The DBT helper commands already committed in projects 02 and 03 are PowerShell scripts under each project's `dbt/scripts/` directory.

## How to Run Each Case

### 01. Hospital Analytics

Full local path from raw data to dashboard:

```powershell
python projects/01-hospital-analytics/src/jobs/run_ingestion.py
python projects/01-hospital-analytics/src/jobs/run_bronze.py
python projects/01-hospital-analytics/src/jobs/run_silver.py
python projects/01-hospital-analytics/src/jobs/run_gold.py
python projects/01-hospital-analytics/src/jobs/run_serving.py
python projects/01-hospital-analytics/api/app.py
```

Then start the dashboard:

```powershell
cd projects/01-hospital-analytics/dashboard
if (!(Test-Path .env)) { Copy-Item .env.example .env }
npm install
npm run dev
```

Default local API base URL:

```text
http://127.0.0.1:5000
```

### 02. Job Market Analytics

Build the Python medallion outputs first:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
python projects/02-job-market-analytics/src/jobs/run_silver.py
python projects/02-job-market-analytics/src/jobs/run_gold.py
```

For the full PostgreSQL-backed mart, API, and dashboard path:

```powershell
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
cd ../../..
python projects/02-job-market-analytics/api/app.py
```

Then start the dashboard:

```powershell
cd projects/02-job-market-analytics/dashboard
Copy-Item .env.example .env
npm install
npm run dev
```

Default local API base URL:

```text
http://127.0.0.1:5001
```

Local DuckDB modeling is also implemented through:

```powershell
cd projects/02-job-market-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
```

### 03. Retail Revenue Analytics

Implemented layered flow:

```text
ingestion -> Bronze -> Silver -> Gold -> DBT DuckDB marts -> Flask API -> React dashboard
```

Run the full local path:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
cd projects/03-retail-revenue-analytics/dbt
.\scripts\run_dbt_duckdb.ps1 debug
.\scripts\run_dbt_duckdb.ps1 run
.\scripts\run_dbt_duckdb.ps1 test
cd ../../..
python projects/03-retail-revenue-analytics/api/app.py
```

Then start the dashboard:

```powershell
cd projects/03-retail-revenue-analytics/dashboard
Copy-Item .env.example .env
npm install
npm run dev
```

Default local API base URL:

```text
http://127.0.0.1:5002
```

Use `http://`, not `https://`, for the local API URL in project 03.

## What The Portfolio Proves Today

Today, this repository proves that the portfolio can support more than one kind of analytics product while keeping a consistent local review workflow.

It currently demonstrates:

- three distinct analytical domains, not one repeated project with renamed labels;
- medallion-style processing across all three cases;
- API and dashboard delivery in all three cases;
- a stronger SQL and DBT modeling layer in project 02 than in project 01;
- the clearest fact-and-dimension analytics-serving pattern in project 03.

For recruiter review, the progression is the important part:

- **Project 01:** proves end-to-end delivery.
- **Project 02:** proves stronger SQL and DBT modeling.
- **Project 03:** proves the strongest dimensional modeling and analytical serving pattern in the portfolio.

## Roadmap

Likely next steps across the portfolio:

- orchestration once the local workflows are stable enough to justify it;
- broader automated validation and CI;
- richer architecture and lineage assets where they reflect real implementations;
- deployment and infrastructure notes only after real deployed environments exist;
- deeper marts and analytical contracts where requirements justify them.

These are roadmap items, not implemented guarantees.

## Honesty / Non-Claims

To keep the portfolio technically credible:

- these are local-first portfolio projects;
- no production deployment is claimed at the repository level;
- no enterprise authentication, authorization, multi-tenant security, or infrastructure maturity is claimed unless explicitly documented in a project;
- roadmap items are future work, not present features;
- project 03 revenue outputs are analytical item-side measures, not accounting-grade revenue;
- project 03 payment summaries are intended for payment-behavior analysis and are modeled carefully to avoid naive duplication.
