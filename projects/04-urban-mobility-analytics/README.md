# Urban Mobility Analytics

Local-first batch analytics case study built on the official NYC TLC Trip Record Data, with a focus on orchestration, incremental month-based ingestion, partitioned Parquet storage, and readable pipeline operations metadata.

This is the fourth portfolio case in the repository. It is intentionally not a dashboard project, not an API project, and not a production deployment claim. The goal here is to prove a stronger local data pipeline operations story over a widely recognized public dataset.

## Why This Case Exists

The first three portfolio projects already prove several end-to-end patterns:

- `01-hospital-analytics`: ingestion, Bronze/Silver/Gold, PostgreSQL serving, API, dashboard.
- `02-job-market-analytics`: Python medallion processing, DBT DuckDB/PostgreSQL, marts, API, dashboard.
- `03-retail-revenue-analytics`: multi-table retail modeling, cautious Gold outputs, DBT dimensional marts, API, dashboard, Docker-assisted demo packaging.

This fourth case complements them by leaning into a different proof point:

- orchestration-first pipeline design;
- official public-source month planning instead of Kaggle rehosting;
- incremental local landing with state manifests;
- partition-aware Parquet outputs;
- rerunnable batch execution with readable metadata;
- local analytical engineering without needing a dashboard layer first.

## Source Choice

This project uses the official NYC Taxi and Limousine Commission Trip Record Data for Yellow Taxi trips.

- Source landing page: `https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page`
- Yellow Taxi data dictionary: `https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf`
- Monthly file pattern: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_YYYY-MM.parquet`

This is a strong source because it is public, widely recognized, analytically rich, and naturally organized as month-based files that support incremental batch ingestion.

## What Is Implemented Now

- official-source Yellow Taxi monthly ingestion;
- configurable month window selection;
- Bronze raw landing into partition-aware local directories;
- readable JSON state tracking for landed and processed months;
- Bronze metadata and raw inventory summaries;
- Silver row-preserving standardization into partitioned Parquet;
- first Gold operational summaries built from Silver with DuckDB;
- local Prefect flow orchestration with real task boundaries;
- lightweight unit tests for stable logic;
- a validation notebook for source inspection.

## Architecture Flow

```text
Official NYC TLC monthly Parquet
-> Bronze raw landing by source month
-> Bronze metadata and inventory
-> Silver standardized trip table in partitioned Parquet
-> Gold monthly operational summaries in partitioned Parquet
-> Local metadata and state artifacts for reruns and inspection
```

## Project Positioning

This case is:

- local-first;
- batch-oriented;
- orchestration-focused;
- incremental by month;
- partition-aware;
- portfolio-grade, but not production-hardened.

This case is not:

- a dashboard implementation;
- a read API;
- a cloud deployment;
- a streaming pipeline;
- a Spark project.

## Default Scope

The default configuration keeps the project practical for local execution:

- default start month: `2024-01`
- default end month: `2024-02`

That gives a small, reproducible baseline while leaving a clear path for future month-by-month extension.

## Local Storage Layout

```text
data/
|-- bronze/
|   |-- raw/
|   |   `-- yellow_taxi/year=YYYY/month=MM/source.parquet
|   |-- metadata/
|   `-- state/
|-- silver/
|   |-- tables/
|   |   `-- trips/pickup_year=YYYY/pickup_month=MM/yellow_taxi_trips_YYYY-MM.parquet
|   |-- metadata/
|   `-- state/
`-- gold/
    |-- tables/
    |   |-- daily_trip_summary/...
    |   |-- hourly_trip_summary/...
    |   |-- payment_type_summary/...
    |   |-- trip_distance_summary/...
    |   `-- fare_amount_summary/...
    |-- metadata/
    `-- state/
```

The generated Parquet and JSON artifacts remain local and inspectable.

## Incremental Strategy

Incremental in this project means month-based rerunnable processing with readable local state files.

- ingestion tracks completed source-month downloads;
- Bronze metadata tracks profiled months;
- Silver tracks standardized months and rewrites only the selected month outputs when forced;
- Gold tracks aggregated months and rewrites only the selected month outputs when forced;
- reruns skip completed months by default;
- `--force` allows a selected month window to be rebuilt.

State files live under:

- `data/bronze/state/ingestion_state.json`
- `data/bronze/state/bronze_state.json`
- `data/silver/state/silver_state.json`
- `data/gold/state/gold_state.json`

## Orchestration

The orchestration layer uses Prefect in a local-first way only.

Implemented flow tasks:

- source month planning;
- official file landing;
- Bronze metadata generation;
- Silver standardization;
- Gold summary generation.

The flow is callable locally from the command line and does not assume Prefect Cloud, a server deployment, or scheduled infrastructure.

## Gold Outputs

Gold currently produces practical monthly operational summaries:

- `daily_trip_summary`
- `hourly_trip_summary`
- `payment_type_summary`
- `trip_distance_summary`
- `fare_amount_summary`

Core KPIs include:

- trip count;
- passenger count sum;
- total fare amount;
- total tip amount;
- total tolls amount;
- average trip distance;
- average total amount;
- average fare amount.

## Setup

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
```

If your shell exposes only `python3`, use that interpreter while keeping the same file paths.

## Run Manually

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_ingestion.py
python projects/04-urban-mobility-analytics/src/jobs/run_bronze.py
python projects/04-urban-mobility-analytics/src/jobs/run_silver.py
python projects/04-urban-mobility-analytics/src/jobs/run_gold.py
```

Override the default month window when needed:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_ingestion.py --start-month 2024-03 --end-month 2024-04
python projects/04-urban-mobility-analytics/src/jobs/run_silver.py --start-month 2024-03 --end-month 2024-04 --force
```

## Run The Prefect Flow

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

Or with explicit bounds:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py --start-month 2024-01 --end-month 2024-02
```

## Documentation

- [Documentation index](docs/README.md)
- [Source notes](docs/source.md)
- [Bronze layer](docs/bronze.md)
- [Silver layer](docs/silver.md)
- [Gold layer](docs/gold.md)
- [Orchestration](docs/orchestration.md)
- [Incremental model](docs/incremental.md)
- [Data layout](data/README.md)

## Current Limitations

- The project does not yet include Taxi Zone enrichment.
- The current scope focuses on Yellow Taxi only.
- Quality checks are lightweight and metadata-oriented, not a full assertion framework.
- The pipeline is local-first and not optimized for very large historical backfills.
- Prefect is used as a local orchestration surface, not a deployed scheduler.
- There is no serving layer, DBT layer, dashboard, or API in this phase.

## Future Directions

- add Taxi Zone lookup enrichment;
- add stronger data quality assertions and anomaly checks;
- add DBT marts over the Silver and Gold outputs when that modeling layer becomes the next proof point;
- add scheduled orchestration and observability later if the portfolio case needs it;
- add a serving or visualization layer only if a later phase clearly benefits from it.
