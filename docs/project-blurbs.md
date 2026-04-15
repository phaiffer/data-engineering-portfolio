# Project Blurbs

Reusable project descriptions for GitHub summaries, project cards, interview notes, and profile material.

## 01 - Hospital Analytics

Path: `projects/01-hospital-analytics/`

### One-Liner

Hospital Analytics is the portfolio's clearest end-to-end local analytics product flow, moving from ingestion through Bronze/Silver/Gold into PostgreSQL, a Flask API, and a React dashboard.

### Short Blurb

This project turns a hospital patient-flow dataset into a reviewable local analytics product. It covers ingestion, medallion-style processing, PostgreSQL serving, a read API, and a dashboard. In the portfolio, it is the best example of complete delivery from raw data to frontend consumption.

### Medium Blurb

Hospital Analytics is the foundation case in the repository. It shows how a local dataset can move through Bronze, Silver, and Gold processing, land in PostgreSQL serving tables and views, and then power a Flask API and React dashboard. Compared with the later projects, it is less focused on advanced modeling depth, but it is the strongest example of full-path analytics delivery.

### What It Proves

- Raw ingestion into a local analytics workflow.
- Bronze, Silver, and Gold layer separation.
- PostgreSQL as a local serving layer.
- Flask API endpoints over curated outputs.
- React dashboard consumption of a real API.
- A complete local review path from source data to frontend.

### Why It Matters in the Portfolio

This project gives the portfolio a clear starting point: it proves that the repository can deliver a real end-to-end analytics experience, not just isolated transformation scripts. That makes the later projects easier to position because they build from a visible delivery baseline instead of starting from abstractions alone.

## 02 - Job Market Analytics

Path: `projects/02-job-market-analytics/`

### One-Liner

Job Market Analytics extends the portfolio into stronger SQL and DBT modeling with DuckDB and PostgreSQL mart paths, plus a read-only API and dashboard.

### Short Blurb

This project analyzes labor-market and AI-impact data through Python medallion processing and DBT-based modeling. It introduces dual DBT targets, relational marts, and a cleaner separation between transformation logic and served analytical outputs. In the portfolio, it is the clearest step up from end-to-end delivery into stronger SQL and DBT work.

### Medium Blurb

Job Market Analytics is the bridge case between project 01's delivery-first structure and project 03's stronger dimensional-modeling story. It keeps a local API and dashboard review surface, but the distinguishing feature is the DBT layer: DuckDB for fast local modeling and PostgreSQL for served marts. That makes it the best project to reference when the conversation shifts toward SQL structure, model layering, and DBT workflow rather than just pipeline execution.

### What It Proves

- Python Bronze, Silver, and Gold processing.
- DBT DuckDB modeling over local artifacts.
- DBT PostgreSQL modeling over loaded Silver data.
- Mart-oriented SQL design stronger than project 01.
- Read-only API patterns over modeled outputs.
- Dashboard consumption over DBT-backed analytical data.

### Why It Matters in the Portfolio

This project shows that the portfolio is not limited to Python-first pipelines with a dashboard at the end. It proves a more mature modeling layer and makes the progression toward dimensional thinking in project 03 feel deliberate rather than abrupt.

## 03 - Retail Revenue Analytics

Path: `projects/03-retail-revenue-analytics/`

### One-Liner

Retail Revenue Analytics is the strongest dimensional-modeling and analytics-serving case in the portfolio, combining a multi-table retail source, DBT DuckDB marts, a read-only API, a dashboard, and Docker-assisted demo packaging.

### Short Blurb

This project uses the Olist retail dataset to show a more realistic modeling problem than a single flat file. It preserves source-aligned Silver tables, builds fact and dimension style marts in DBT, and serves those modeled outputs through an API and dashboard. Revenue is positioned for analytical use, not as accounting-grade reporting.

### Medium Blurb

Retail Revenue Analytics is the strongest analytics-engineering case in the repository for dimensional design and business-facing serving. The project starts with a multi-table retail source, keeps Silver aligned to source tables, produces first-pass Gold KPI summaries, and then builds DBT DuckDB staging, intermediate, and mart layers centered on `fct_sales` and supporting dimensions. It also adds a read-only Flask API, a React dashboard, and a Docker-assisted local demo path, making it the best project to inspect for fact/dimension modeling and analytical serving together.

### What It Proves

- Multi-table source handling across retail entities such as orders, items, payments, products, customers, and sellers.
- Source-aligned Silver design instead of premature flattening.
- DBT staging, intermediate, and mart layering in DuckDB.
- Fact plus dimension style modeling for business-facing analytics.
- Read-only API delivery over modeled marts.
- Dashboard consumption and Docker-assisted demo packaging.

### Why It Matters in the Portfolio

This project gives the portfolio its strongest dimensional-modeling case and its clearest analytics-serving story. It is also the best example of staying technically credible while still being portfolio-friendly, because it includes an explicit caveat that revenue is analytical item-side reporting rather than accounting-grade finance.

## 04 - Urban Mobility Analytics

Path: `projects/04-urban-mobility-analytics/`

### One-Liner

Urban Mobility Analytics is the portfolio's strongest orchestration and incremental pipeline case, built on official NYC TLC Yellow Taxi data with month-based processing, partitioned Parquet outputs, and local Prefect orchestration.

### Short Blurb

This project focuses on pipeline operations rather than APIs or dashboards. It ingests official monthly Yellow Taxi files, tracks progress with readable JSON state, standardizes data into partitioned Parquet, and runs through a local Prefect flow. In the portfolio, it is the clearest example of incremental execution and partition-aware batch design.

### Medium Blurb

Urban Mobility Analytics is the portfolio's strongest proof point for orchestration and local batch pipeline operations. Instead of repeating the serving pattern from the first three projects, it uses official NYC TLC monthly files to demonstrate incremental month-based ingestion, partition-aware Bronze/Silver/Gold outputs, readable state tracking, and rerunnable Prefect-managed flow execution. The absence of an API or dashboard in this phase is intentional: the project's value is in pipeline behavior, not presentation-layer breadth.

### What It Proves

- Official public-source ingestion from NYC TLC Yellow Taxi data.
- Month-based incremental execution over a selected review window.
- Partitioned Parquet outputs across Bronze, Silver, and Gold.
- Readable JSON state tracking for reruns and inspection.
- Local-first Prefect orchestration with real task boundaries.
- A pipeline-operations case that is materially different from the serving-oriented projects.

### Why It Matters in the Portfolio

This project prevents the portfolio from reading like three variations of the same dashboard pattern. It shows that the work also covers orchestration, incremental processing, partition-aware storage, and rerunnable local data operations, which broadens the technical story in a grounded way.
