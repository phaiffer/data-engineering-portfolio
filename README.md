# Data Engineering Portfolio

`phaiffer/data-engineering-portfolio` is a portfolio of six complementary data engineering and analytics engineering case studies.

The projects are intentionally not all solving the same problem. Together they show progression across local ingestion, medallion processing, SQL and dbt modeling, dimensional marts, analytics serving, orchestration, incremental batch design, streaming and replay, and warehouse-first BigQuery analytics.

## Start Here

Choose the project based on what you want to evaluate:

| If you want to review... | Start with | Why |
|---|---|---|
| Raw data to dashboard | [`01-hospital-analytics`](projects/01-hospital-analytics/) | Clearest end-to-end local analytics product flow |
| SQL and dbt modeling paths | [`02-job-market-analytics`](projects/02-job-market-analytics/) | Bridges Python medallion processing with DuckDB and PostgreSQL dbt marts |
| Dimensional modeling and analytics serving | [`03-retail-revenue-analytics`](projects/03-retail-revenue-analytics/) | Strongest fact/dimension, KPI, API, and dashboard case |
| Orchestration and incremental batch pipelines | [`04-urban-mobility-analytics`](projects/04-urban-mobility-analytics/) | Strongest Prefect, state, rerun, and partition-aware case |
| Streaming, broker boundaries, checkpoints, replay | [`05-event-stream-analytics`](projects/05-event-stream-analytics/) | Strongest Redpanda-backed local streaming and replay-aware case |
| Warehouse-first analytics engineering | [`06-warehouse-first-analytics`](projects/06-warehouse-first-analytics/) | Strongest dbt BigQuery, managed-warehouse, and cost-aware modeling case |

Projects 03 through 06 include stronger reviewer guidance, Windows-native run paths, and validation-oriented documentation in their project READMEs and `docs/` folders.

## Portfolio Narrative

This repository exists to show practical data engineering work in a format that is easy to inspect. It is not presented as a single production platform. The value is in clear project boundaries, credible local or warehouse-native run paths, readable analytical layers, and honest scope discipline.

The progression is deliberate:

- **Project 01** proves that raw data can move through local analytical layers into a served API and dashboard.
- **Project 02** adds stronger SQL and dbt modeling patterns across DuckDB and PostgreSQL.
- **Project 03** deepens the analytics-serving story with a richer multi-table source, fact/dimension design, KPI marts, API, dashboard, and Docker-assisted review path.
- **Project 04** pivots away from serving and focuses on official public batch data, orchestration, incremental month windows, partitioned Parquet, state, and reruns.
- **Project 05** shifts to event-driven architecture with a local broker, producer/consumer separation, checkpoints, Bronze landing, and replay-aware rebuilds.
- **Project 06** removes local ingestion entirely and focuses on dbt BigQuery modeling, managed warehouse marts, tests, docs, and cost-aware query design.

## Project Summaries

### 01. Hospital Analytics

**Role:** foundation end-to-end local analytics case.

**Domain:** hospital patient flow and operational reporting.

**What it proves:**

- ingestion through Bronze, Silver, and Gold processing;
- PostgreSQL as a local serving layer;
- Flask API endpoints over served outputs;
- React dashboard consumption;
- complete local raw-to-dashboard review path.

**Positioning:** best first stop for evaluating the repository's end-to-end delivery foundation. It is intentionally less modeling-heavy than projects 02 and 03.

### 02. Job Market Analytics

**Role:** SQL and dbt modeling bridge.

**Domain:** labor-market and AI-impact analytics.

**What it proves:**

- Python medallion processing;
- dbt DuckDB and dbt PostgreSQL modeling paths;
- mart-style SQL modeling over standardized data;
- read-only API and dashboard over modeled outputs.

**Positioning:** stronger SQL/dbt proof than project 01, but not the deepest dimensional modeling or warehouse-first case.

### 03. Retail Revenue Analytics

**Role:** strongest dimensional-modeling and analytics-serving case.

**Domain:** retail and e-commerce revenue analytics using the Olist dataset.

**What it proves:**

- multi-table source handling across orders, items, payments, products, customers, sellers, and reviews;
- source-aligned Silver tables;
- dbt DuckDB staging, intermediate, and mart layers;
- fact table plus supporting dimensions;
- business-facing KPI marts;
- read-only Flask API and React dashboard over modeled outputs;
- Docker-assisted and Windows-friendly local review paths.

**Positioning:** best project for evaluating dimensional thinking, KPI design, mart contracts, and a thin analytics serving layer. It does not claim accounting-grade revenue or production deployment.

### 04. Urban Mobility Analytics

**Role:** strongest orchestration, incremental batch, state, and partition-aware pipeline case.

**Domain:** NYC Yellow Taxi trip analytics.

**What it proves:**

- official public-source ingestion from NYC TLC monthly files;
- month-based incremental execution;
- partitioned Bronze, Silver, and Gold Parquet outputs;
- readable JSON state for reruns and inspection;
- Prefect orchestration with meaningful task boundaries;
- validation and reviewer guidance without adding an API or dashboard.

**Positioning:** best project for reviewing batch operations, rerun behavior, state management, and partition-aware processing. It is a local-first orchestration case, not a production scheduler claim.

### 05. Event Stream Analytics

**Role:** strongest broker-backed, checkpoint-aware, replay-aware streaming case.

**Domain:** Wikimedia RecentChange event stream analytics.

**What it proves:**

- bounded live capture from the official Wikimedia SSE stream;
- Redpanda broker decoupling between publisher and Bronze consumer;
- explicit producer and consumer boundaries;
- raw Bronze JSONL landing with readable checkpoints;
- partitioned Silver Parquet and local Gold analytical summaries;
- clear distinction between broker replay and offline replay from landed Bronze;
- local validation manifest and reviewer-oriented inspection surface.

**Positioning:** best project for reviewing streaming architecture, checkpoints, broker retention tradeoffs, duplicate risk, and safe downstream replay. It is not a dashboard, API, or production streaming platform case.

### 06. Warehouse-First Analytics

**Role:** strongest warehouse-first, dbt BigQuery, cost-aware analytics engineering case.

**Domain:** Stack Overflow developer ecosystem analytics.

**What it proves:**

- dbt BigQuery workflow over `bigquery-public-data.stackoverflow`;
- warehouse-native source inspection without local ingestion;
- staging views, intermediate views, and mart tables;
- marts for monthly activity, tag activity, answer latency, question outcomes, and user reputation segments;
- dbt schema tests, singular tests, and docs as first-class artifacts;
- cost-aware design through a year-window variable, selective columns, view/table materialization choices, and cheaper development loops;
- Windows-friendly BigQuery authentication and dbt validation guidance.

**Positioning:** best project for evaluating managed-warehouse analytics engineering. It is not a local ingestion, API, dashboard, or production BigQuery governance platform.

## Capability Matrix

| Case | Main proof point | Source style | Modeling | Serving | Operations / validation |
|---|---|---|---|---|---|
| [`01-hospital-analytics`](projects/01-hospital-analytics/) | End-to-end local analytics | Kaggle local files | Bronze/Silver/Gold, limited dbt scaffold | PostgreSQL, Flask, React | Local pipeline and dashboard review |
| [`02-job-market-analytics`](projects/02-job-market-analytics/) | SQL and dbt modeling bridge | Kaggle local files | Python medallion, dbt DuckDB + PostgreSQL marts | Flask, React | Local dbt and API/dashboard review |
| [`03-retail-revenue-analytics`](projects/03-retail-revenue-analytics/) | Dimensional modeling and analytics serving | Kaggle multi-table source | Source-aligned Silver, fact + dimensions, dbt marts | Flask, React, Docker-assisted demo | Reviewer guide, Windows scripts, API smoke checks |
| [`04-urban-mobility-analytics`](projects/04-urban-mobility-analytics/) | Orchestrated incremental batch | Official NYC TLC monthly files | Partitioned Bronze/Silver/Gold Parquet | None by design | Prefect flow, JSON state, rerun and validation docs |
| [`05-event-stream-analytics`](projects/05-event-stream-analytics/) | Broker-backed streaming and replay | Official Wikimedia live SSE stream | Bronze JSONL, Silver Parquet, Gold summaries | None by design | Redpanda, checkpoints, replay notes, validation manifest |
| [`06-warehouse-first-analytics`](projects/06-warehouse-first-analytics/) | Warehouse-first analytics engineering | BigQuery public dataset | dbt BigQuery staging/intermediate/marts | None by design | dbt debug/deps/run/test/docs, mart queries, cost notes |

## Repository Structure

```text
data-engineering-portfolio/
|-- projects/
|   |-- 01-hospital-analytics/
|   |-- 02-job-market-analytics/
|   |-- 03-retail-revenue-analytics/
|   |-- 04-urban-mobility-analytics/
|   |-- 05-event-stream-analytics/
|   `-- 06-warehouse-first-analytics/
|-- docs/
|-- shared/
|-- requirements.txt
`-- requirements-dev.txt
```

## Local Setup

Most projects are local-first and can be reviewed from a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install project-specific requirements only when reviewing that project. For example:

```bash
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
python -m pip install -r projects/05-event-stream-analytics/requirements.txt
python -m pip install -r projects/06-warehouse-first-analytics/dbt/requirements.txt
```

High-level dependency notes:

- projects 01, 02, and 03 use Node.js for their dashboard layers;
- projects 01 and 02 use PostgreSQL for their served local review path;
- project 03 includes a Docker-assisted API/dashboard demo path;
- project 04 uses Prefect locally for orchestration;
- project 05 requires Docker for the local Redpanda broker;
- project 06 requires Google Cloud CLI, BigQuery API access, and dbt BigQuery credentials.

Each project README contains the authoritative run path for that case. Projects 03, 04, 05, and 06 now include reviewer-oriented docs and Windows-native helper scripts where appropriate.

## How To Run Each Case

Keep root-level execution guidance high-level. Use the project READMEs for exact commands, environment variables, and validation steps.

| Case | Primary run documentation | Notes |
|---|---|---|
| 01 | [`projects/01-hospital-analytics/README.md`](projects/01-hospital-analytics/README.md) | Local PostgreSQL, Flask API, React dashboard |
| 02 | [`projects/02-job-market-analytics/README.md`](projects/02-job-market-analytics/README.md) | Python medallion flow, dbt DuckDB/PostgreSQL, API, dashboard |
| 03 | [`projects/03-retail-revenue-analytics/README.md`](projects/03-retail-revenue-analytics/README.md) | Dimensional marts, API/dashboard, Docker-assisted review, Windows scripts |
| 04 | [`projects/04-urban-mobility-analytics/README.md`](projects/04-urban-mobility-analytics/README.md) | Prefect flow, incremental month windows, partition/state validation |
| 05 | [`projects/05-event-stream-analytics/README.md`](projects/05-event-stream-analytics/README.md) | Redpanda broker, publisher/consumer, replay, validation manifest |
| 06 | [`projects/06-warehouse-first-analytics/README.md`](projects/06-warehouse-first-analytics/README.md) | dbt BigQuery, mart inspection queries, cost-aware validation |

## What The Portfolio Proves Today

Today this repository shows six different but connected proof points:

- local raw-to-dashboard delivery;
- SQL and dbt modeling across local analytical stores;
- dimensional modeling and analytics-serving patterns;
- orchestration, incremental processing, partitioning, state, and reruns;
- broker-backed streaming, checkpoints, and replay-aware design;
- warehouse-first analytics engineering in BigQuery with dbt tests, docs, and cost-aware modeling.

The portfolio shows breadth without pretending every project has the same goal, maturity level, or serving surface.

## Roadmap

Future work across the portfolio may include:

- richer observability beyond current local-first instrumentation;
- broader automated validation and CI;
- cloud deployment notes only when real deployed environments exist;
- serving layers only where justified by a concrete review or product use case;
- stronger warehouse governance, docs, and dbt exposures if later needed;
- streaming-to-serving scenarios if later justified by a concrete use case.

These are future directions, not implemented repository-wide guarantees.

## Honesty / Non-Claims

To keep the portfolio technically credible:

- this is a portfolio of case studies, not a repository-level production platform claim;
- no enterprise authentication, authorization, infrastructure maturity, or operational SLA claim is made unless a project explicitly documents it;
- roadmap items are future work, not present features;
- project 03 revenue outputs are analytical item-side measures, not accounting-grade revenue;
- project 04 orchestration is a local-first Prefect implementation, not a claim of a production scheduler or data platform;
- project 05 is a bounded local streaming case; it is not a claim of a production streaming platform, exactly-once delivery guarantees, or cloud infrastructure maturity;
- project 06 is a warehouse-first portfolio case; it is not a claim of a production BigQuery platform, enterprise warehouse governance setup, or scheduled cloud deployment;
- projects without an API or dashboard are intentionally scoped that way rather than presented as unfinished production systems.
