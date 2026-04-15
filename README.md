# Data Engineering Portfolio

`phaiffer/data-engineering-portfolio` is a local-first portfolio of five complementary analytics case studies:

- [`projects/01-hospital-analytics/`](projects/01-hospital-analytics/)
- [`projects/02-job-market-analytics/`](projects/02-job-market-analytics/)
- [`projects/03-retail-revenue-analytics/`](projects/03-retail-revenue-analytics/)
- [`projects/04-urban-mobility-analytics/`](projects/04-urban-mobility-analytics/)
- [`projects/05-event-stream-analytics/`](projects/05-event-stream-analytics/)

Together they show a clear progression:

- project 01 proves end-to-end local analytics delivery;
- project 02 strengthens the SQL and DBT modeling story;
- project 03 is the strongest dimensional-modeling and analytics-serving case;
- project 04 is the strongest orchestration, incremental, and partition-aware pipeline case;
- project 05 is the strongest event-driven, broker-based, and replayable stream pipeline case.

In a quick review, this README should make it easy to understand what the repository is, what each project proves, how the projects differ, how to run them locally, and what is implemented today versus what is still roadmap.

## Why This Portfolio Exists

This repository exists to show practical data engineering work in a format that is easy to inspect locally.

It is not presented as a production platform. The value is in clear analytical layers, credible local run paths, readable project boundaries, and small but real serving surfaces where they already exist.

Across the portfolio, recurring themes include:

- medallion-style processing;
- explicit boundaries between raw, standardized, and analytical layers;
- lightweight APIs and dashboards where they add review value;
- incremental improvement from one case study to the next without pretending every project solves the same problem.

## Portfolio Case Studies Overview

- [`01-hospital-analytics`](projects/01-hospital-analytics/): the foundation end-to-end case, from ingestion to PostgreSQL, Flask, and React.
- [`02-job-market-analytics`](projects/02-job-market-analytics/): a stronger SQL and DBT case with DuckDB and PostgreSQL modeling paths.
- [`03-retail-revenue-analytics`](projects/03-retail-revenue-analytics/): the strongest fact/dimension and analytics-serving case, backed by a richer multi-table retail source.
- [`04-urban-mobility-analytics`](projects/04-urban-mobility-analytics/): the strongest orchestration and incremental batch pipeline case, built around official monthly NYC TLC data.
- [`05-event-stream-analytics`](projects/05-event-stream-analytics/): the strongest event-driven and replayable stream pipeline case, built on the official Wikimedia EventStreams RecentChange feed via Redpanda.

## Case-by-Case Breakdown

### Project 01 - Hospital Analytics

**Domain:** hospital patient flow and operational reporting.

**What it proves:**

- ingestion plus Bronze, Silver, and Gold processing;
- PostgreSQL as a local serving layer;
- Flask API endpoints over served outputs;
- React dashboard consumption;
- a complete local analytics product flow from raw data to a reviewable frontend.

**How it is positioned:**

This is the clearest proof that the portfolio can deliver an end-to-end local analytics experience. It is less modeling-heavy than projects 02 and 03, but it is the best "raw data to dashboard" foundation case.

### Project 02 - Job Market Analytics

**Domain:** labor-market and AI-impact analytics.

**What it proves:**

- Python medallion processing;
- DBT DuckDB and DBT PostgreSQL modeling paths;
- mart-style SQL modeling over standardized data;
- read-only API patterns;
- dashboard delivery over modeled outputs.

**How it is positioned:**

This is the bridge between project 01's end-to-end delivery story and project 03's stronger dimensional-modeling story. It proves materially stronger SQL and DBT work than project 01 without overclaiming full warehouse maturity.

### Project 03 - Retail Revenue Analytics

**Domain:** retail and e-commerce revenue analytics using the Olist dataset.

**Why the source matters:**

Olist lands as multiple related tables such as orders, order items, payments, products, customers, and sellers. That makes it a better portfolio case for source-aligned Silver design, careful joins, and dimensional marts than a single flat-file source.

**What it proves:**

- multi-table retail source handling;
- source-aligned Silver tables;
- Gold KPI summaries for first-pass business review;
- DBT DuckDB staging, intermediate, and mart layers;
- fact plus supporting dimensions;
- read-only API endpoints over modeled marts;
- dashboard consumption over the API;
- Docker-assisted demo packaging for local review.

**How it is positioned:**

Project 03 is the strongest dimensional-modeling and analytics-serving case in the repository today. It is the clearest example of fact-and-dimension thinking, business-facing marts, and a thin serving layer over modeled outputs.

### Project 04 - Urban Mobility Analytics

**Domain:** urban mobility analytics built around Yellow Taxi trip data.

**Source:** official NYC TLC Yellow Taxi trip records.

**Why the source matters:**

Unlike the earlier Kaggle-based cases, this project uses an official public source with naturally month-based files. That makes it a better fit for incremental ingestion planning, rerunnable monthly processing, and partition-aware local storage.

**What it proves:**

- official public-source ingestion;
- month-based incremental pipeline design;
- partitioned Parquet outputs in Bronze, Silver, and Gold;
- readable JSON state tracking for reruns and inspection;
- Prefect orchestration with real task boundaries;
- local-first batch pipeline operations over a recognizable public dataset.

**How it is positioned:**

Project 04 is materially different from the first three cases. It does not add an API or dashboard in this phase. Instead, it focuses on orchestration, incremental execution, partition-aware storage, and rerun behavior. It is the strongest orchestration and pipeline-operations case in the portfolio today, without claiming to be a production scheduler or platform.

### Project 05 - Event Stream Analytics

**Domain:** event stream analytics built on the official Wikimedia EventStreams RecentChange feed.

**Source:** official Wikimedia SSE stream (`stream.wikimedia.org/v2/stream/recentchange`).

**Why the source matters:**

Unlike the batch files used in projects 01 through 04, this source is a live public event stream. That makes it a natural fit for broker-backed ingestion, bounded local capture, checkpointing, and replay-aware pipeline design. The engineering story is fundamentally different from any of the earlier cases.

**What it proves:**

- event-driven ingestion via a live public SSE stream;
- Redpanda message broker decoupling publisher from consumer;
- explicit producer and consumer boundaries;
- Bronze raw JSONL landing with readable checkpoint artifacts;
- Silver row-preserving standardization into partitioned Parquet;
- Gold category and minute-bucket analytical summaries rebuilt from Silver;
- offline replay from landed Bronze, which stays reproducible after broker retention moves on;
- local-first, bounded, and inspectable throughout.

**How it is positioned:**

Project 05 is the event-driven complement to the batch-first cases. It does not add a dashboard or API in this phase. Instead, it focuses on broker-based ingestion architecture, checkpointing, and replay-aware pipeline design. It is the strongest streaming and event-pipeline case in the portfolio, without claiming to be a production streaming platform.

## Comparison / Capability Matrix

| Case | Domain | Ingestion | Bronze | Silver | Gold | DBT | Warehouse / DB | API | Dashboard | Dimensional Modeling | Orchestration | Incremental / Partitioned | Streaming / Event-Driven |
| ---- | ------ | --------- | ------ | ------ | ---- | --- | -------------- | --- | --------- | -------------------- | ------------- | ------------------------- | ------------------------ |
| [`01-hospital-analytics`](projects/01-hospital-analytics/) | Hospital operations | Kaggle to local raw files | Yes | Yes | Yes | Scaffold only | PostgreSQL serving layer | Flask | React | Limited; not the main focus | No | No | No |
| [`02-job-market-analytics`](projects/02-job-market-analytics/) | Job market / AI impact | Kaggle to local raw files | Yes | Yes | Yes | DuckDB + PostgreSQL marts | DuckDB + PostgreSQL | Read-only Flask | React | Moderate; stronger marts than 01 | No | No | No |
| [`03-retail-revenue-analytics`](projects/03-retail-revenue-analytics/) | Retail / e-commerce | Kaggle multi-table source | Yes | Yes; source-aligned tables | Yes | DuckDB staging, intermediate, and marts | DuckDB | Read-only Flask | React | Strongest; fact + dimensions | No | No | No |
| [`04-urban-mobility-analytics`](projects/04-urban-mobility-analytics/) | Urban mobility / Yellow Taxi | Official NYC TLC monthly files | Yes | Yes; partitioned Parquet | Yes; partitioned summaries | No | DuckDB for local Gold aggregation | No | No | Not the main focus in this phase | Prefect, local-first | Strongest | No |
| [`05-event-stream-analytics`](projects/05-event-stream-analytics/) | Event stream / Wikimedia RecentChange | Official live SSE stream via Redpanda | Yes; raw JSONL landing | Yes; partitioned Parquet | Yes; category and minute-bucket summaries | No | DuckDB for local Gold aggregation | No | No | Not the main focus | Not the main focus | Partitioned; checkpoint-based | Strongest |

## Repository Structure

```text
data-engineering-portfolio/
|-- projects/
|   |-- 01-hospital-analytics/
|   |-- 02-job-market-analytics/
|   |-- 03-retail-revenue-analytics/
|   |-- 04-urban-mobility-analytics/
|   `-- 05-event-stream-analytics/
|-- docs/
|-- shared/
|-- requirements.txt
`-- requirements-dev.txt
```

- `projects/` contains the five portfolio case studies.
- `docs/` contains repository-level notes.
- `shared/` contains templates, conventions, and shared assets.

## Local Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Install project-specific extras only when needed:

```bash
python -m pip install -r projects/02-job-market-analytics/dbt/requirements.txt
python -m pip install -r projects/03-retail-revenue-analytics/dbt/requirements.txt
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
```

Optional repository-wide extras:

```bash
python -m pip install -r requirements-dev.txt
```

Install project-specific extras for project 05:

```bash
python -m pip install -r projects/05-event-stream-analytics/requirements.txt
```

Project 05 also requires Docker to start the local Redpanda broker.

Practical local notes:

- projects 01, 02, and 03 use Node.js for the dashboard layer;
- projects 01 and 02 use PostgreSQL for their served local review path;
- projects 01, 02, and 03 ingest from Kaggle-based sources;
- project 04 pulls from the official public NYC TLC source instead of Kaggle;
- project 05 pulls from the official live Wikimedia SSE stream and requires Docker for the Redpanda broker.

## How to Run Each Case

### 01. Hospital Analytics

Configure local PostgreSQL settings from `projects/01-hospital-analytics/.env.example`, then run:

```bash
python projects/01-hospital-analytics/src/jobs/run_ingestion.py
python projects/01-hospital-analytics/src/jobs/run_bronze.py
python projects/01-hospital-analytics/src/jobs/run_silver.py
python projects/01-hospital-analytics/src/jobs/run_gold.py
python projects/01-hospital-analytics/src/jobs/run_serving.py
python projects/01-hospital-analytics/api/app.py
```

Dashboard:

```bash
cd projects/01-hospital-analytics/dashboard
cp .env.example .env
npm install
npm run dev
```

Default local API base URL: `http://127.0.0.1:5000`

### 02. Job Market Analytics

Configure local PostgreSQL settings from `projects/02-job-market-analytics/.env.example`, then run the Python medallion flow:

```bash
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
python projects/02-job-market-analytics/src/jobs/run_silver.py
python projects/02-job-market-analytics/src/jobs/run_gold.py
python projects/02-job-market-analytics/src/jobs/run_postgres_load.py
```

Run the PostgreSQL DBT path from `projects/02-job-market-analytics/dbt`:

```powershell
.\scripts\run_dbt_postgres.ps1 debug
.\scripts\run_dbt_postgres.ps1 run
.\scripts\run_dbt_postgres.ps1 test
```

Start the API and dashboard:

```bash
python projects/02-job-market-analytics/api/app.py
cd projects/02-job-market-analytics/dashboard
cp .env.example .env
npm install
npm run dev
```

Default local API base URL: `http://127.0.0.1:5001`

DuckDB modeling is also implemented through `projects/02-job-market-analytics/dbt/scripts/run_dbt_duckdb.ps1`.

### 03. Retail Revenue Analytics

Run the layered pipeline and DuckDB marts:

```bash
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
cd projects/03-retail-revenue-analytics/dbt
python -m dbt.cli.main debug --profiles-dir . --target duckdb
python -m dbt.cli.main run --profiles-dir . --target duckdb
python -m dbt.cli.main test --profiles-dir . --target duckdb
cd ../../..
python projects/03-retail-revenue-analytics/api/app.py
```

Dashboard:

```bash
cd projects/03-retail-revenue-analytics/dashboard
cp .env.example .env
npm install
npm run dev
```

Default local API base URL: `http://127.0.0.1:5002`

Project 03 also includes a Docker-assisted demo path:

```bash
cd projects/03-retail-revenue-analytics
docker compose up --build retail-api retail-dashboard
```

### 04. Urban Mobility Analytics

Project 04 has no dashboard or API in this phase. The review surface is the batch pipeline itself plus the generated Parquet and JSON metadata.

Install the project requirements, then run either the jobs individually or the Prefect flow:

```bash
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
python projects/04-urban-mobility-analytics/src/jobs/run_ingestion.py
python projects/04-urban-mobility-analytics/src/jobs/run_bronze.py
python projects/04-urban-mobility-analytics/src/jobs/run_silver.py
python projects/04-urban-mobility-analytics/src/jobs/run_gold.py
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

High-level run path:

```text
ingestion -> Bronze -> Silver -> Gold
```

Orchestration entrypoint:

```text
Prefect flow via projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

The default local review window is `2024-01` through `2024-02`. Override it with `--start-month`, `--end-month`, and `--force` when you want to rerun a selected month range.

### 05. Event Stream Analytics

Project 05 has no dashboard or API in this phase. The review surface is the broker pipeline, the landed Bronze JSONL files, and the Gold analytical summaries.

Start the Redpanda broker:

```bash
cd projects/05-event-stream-analytics
docker compose up -d
```

Run the publisher, Bronze consumer, Silver, and Gold layers:

```bash
python projects/05-event-stream-analytics/src/jobs/run_publisher.py --max-events 100 --max-seconds 60
python projects/05-event-stream-analytics/src/jobs/run_bronze_consumer.py --max-events 100 --max-seconds 60
python projects/05-event-stream-analytics/src/jobs/run_silver.py
python projects/05-event-stream-analytics/src/jobs/run_gold.py
```

Replay Silver and Gold from already-landed Bronze (no live stream or broker required):

```bash
python projects/05-event-stream-analytics/src/jobs/run_replay.py
```

Stop the broker when finished:

```bash
cd projects/05-event-stream-analytics
docker compose down
```

## What The Portfolio Proves Today

Today this repository shows five different but connected proof points:

- **Project 01:** end-to-end local analytics delivery from raw ingestion to PostgreSQL, API, and dashboard.
- **Project 02:** stronger SQL and DBT modeling through DuckDB and PostgreSQL marts.
- **Project 03:** the strongest fact/dimension and analytics-serving pattern in the portfolio.
- **Project 04:** orchestration, incremental execution, partition-aware storage, and readable rerun behavior.
- **Project 05:** event-driven ingestion, broker-based producer/consumer separation, replayable Bronze landing, and local streaming architecture patterns.

Taken together, the portfolio shows breadth without pretending every project has the same goal or maturity level.

## Roadmap

Future work across the portfolio may include:

- richer observability beyond current local-first instrumentation;
- broader automated validation and CI;
- warehouse-first patterns where a future case truly benefits from them;
- streaming-to-serving scenarios if later justified by a concrete use case;
- cloud deployment notes only when real deployed environments exist.

These are future directions, not implemented repository-wide guarantees.

## Honesty / Non-Claims

To keep the portfolio technically credible:

- this is a local-first portfolio, not a repository-level production platform claim;
- no enterprise authentication, authorization, infrastructure maturity, or operational SLA claim is made unless a project explicitly documents it;
- roadmap items are future work, not present features;
- project 03 revenue outputs are analytical item-side measures, not accounting-grade revenue;
- project 04 orchestration is a local-first Prefect implementation, not a claim of a production scheduler or data platform;
- project 05 is a bounded local streaming case; it is not a claim of a production streaming platform, exactly-once delivery guarantees, or cloud infrastructure maturity;
- projects without an API or dashboard are intentionally scoped that way rather than presented as unfinished production systems.
