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

## What To Review First

For a fast technical review, start with these files:

- [Orchestration entrypoint](src/orchestration/flows.py): Prefect flow and task boundaries.
- [Month/state model](src/ingestion/state.py): completed-month tracking, skip behavior, and latest-run metadata shape.
- [Source planning and landing](src/ingestion/sources.py): official TLC URL planning, state-aware downloads, and ingestion run metadata.
- [Silver pipeline](src/processing/silver/pipeline.py): row-preserving standardization and pickup-month partition writes.
- [Gold pipeline](src/processing/gold/pipeline.py): DuckDB summaries over partitioned Silver outputs.
- [Incremental model](docs/incremental.md): reviewer notes for reruns, `--force`, and source-month versus pickup-month semantics.

This project is best evaluated as an orchestration and local batch operations case, not as a dashboard or serving-layer demo.

## Evaluate In 5 Minutes

From the repository root on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt

.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_tests.ps1
```

The first flow run lands and processes the selected month. The second run should return skipped months for completed layers because state files already mark the month complete. Use `-Force` when you want to rebuild the selected month window explicitly.

Key artifacts to inspect after the run:

- `data/bronze/state/ingestion_state.json`
- `data/bronze/metadata/latest_ingestion_run.json`
- `data/bronze/metadata/latest_bronze_run.json`
- `data/silver/metadata/latest_silver_run.json`
- `data/gold/metadata/latest_gold_run.json`
- `data/silver/tables/trips/pickup_year=YYYY/pickup_month=MM/`
- `data/gold/tables/<table_name>/pickup_year=YYYY/pickup_month=MM/`

## Key Operational Insights

- The pipeline planning unit is the official TLC source month.
- State files are keyed by source month, which prevents duplicate downloads and repeated processing on normal reruns.
- Silver and Gold output folders are partitioned by parsed pickup year and month.
- Output filenames retain the source-month identifier, so spillover partitions remain traceable to the original TLC monthly file.
- Latest-run metadata records run timestamps, selected month window, processed months, skipped months, output paths, status, and state paths.
- Silver quality metadata keeps row-count preservation, timestamp nulls, invalid trip durations, negative monetary values, and partition-column expectations visible without turning the project into a full data-quality platform.

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

## Environment Requirements

This project expects a project-compatible Python environment instead of relying on the repository root dependencies alone.

`requirements.txt` includes the packages needed for:

- Pandas and `pyarrow` for the preferred local Parquet notebook path;
- DuckDB for Gold summary generation;
- Prefect for local orchestration;
- `pytest` for the project tests;
- `ipykernel` so the environment can be used directly as a notebook kernel.

Recommended setup from the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
```

Windows PowerShell setup from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r projects/04-urban-mobility-analytics/requirements.txt
```

If you want to use this environment as a dedicated notebook kernel:

```bash
python -m ipykernel install --user --name urban-mobility-analytics --display-name "Urban Mobility Analytics"
```

The notebook prefers Pandas with `pyarrow`. If `pyarrow` is missing but `duckdb` is available in the active kernel, it falls back to DuckDB for local Parquet inspection. If neither path is available, it raises a clear environment error.

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

The partitioning semantics are intentionally split:

- ingestion is planned by source month;
- Silver and Gold are partitioned by resolved pickup year and month;
- filenames still retain the source-month identifier for traceability.

That means a selected source-month file can create a few spillover pickup partitions when the official TLC data includes records whose parsed pickup timestamp falls outside the nominal month. This is treated as a source-data characteristic and is recorded in metadata instead of being silently filtered out.

## Incremental Strategy

Incremental in this project means month-based rerunnable processing with readable local state files.

- ingestion tracks completed source-month downloads;
- Bronze metadata tracks profiled months;
- Silver tracks standardized months and rewrites only the selected month outputs when forced;
- Gold tracks aggregated months and rewrites only the selected month outputs when forced;
- reruns skip completed months by default;
- `--force` allows a selected month window to be rebuilt.

State is tracked by source month even when the resulting Silver and Gold partitions spill into adjacent pickup months.

State files live under:

- `data/bronze/state/ingestion_state.json`
- `data/bronze/state/bronze_state.json`
- `data/silver/state/silver_state.json`
- `data/gold/state/gold_state.json`

Normal reruns read these files before doing work. If a selected month is already marked `completed` for a layer, that layer returns a skipped result for the month and keeps the existing outputs. This keeps local reruns idempotent for the month window.

Forced reruns use `--force` or `-Force` from the PowerShell wrappers. In that mode, the selected month window is processed again. Silver and Gold remove files for the selected source month before rewriting them, which avoids duplicate files while keeping adjacent source-month files intact.

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

If your shell exposes only `python3`, use that interpreter while keeping the same file paths.

## Run Manually

Windows PowerShell wrappers:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_ingestion.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_bronze.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_silver.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_gold.ps1 -StartMonth 2024-01 -EndMonth 2024-01
```

Force a month rebuild from PowerShell:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_silver.ps1 -StartMonth 2024-01 -EndMonth 2024-01 -Force
.\projects\04-urban-mobility-analytics\scripts\run_gold.ps1 -StartMonth 2024-01 -EndMonth 2024-01 -Force
```

Cross-platform Python entrypoints:

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

Windows PowerShell:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-02
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-02 -Force
```

Cross-platform Python:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py
```

Or with explicit bounds:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_flow.py --start-month 2024-01 --end-month 2024-02
```

## Run The Tests

Windows PowerShell:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_tests.ps1
```

Cross-platform Python:

```bash
python -m pytest projects/04-urban-mobility-analytics/tests
```

## Local Validation Examples

Inspect latest-run metadata:

```powershell
Get-Content projects/04-urban-mobility-analytics/data/silver/metadata/latest_silver_run.json
Get-Content projects/04-urban-mobility-analytics/data/gold/metadata/latest_gold_run.json
```

Inspect state files:

```powershell
Get-Content projects/04-urban-mobility-analytics/data/bronze/state/ingestion_state.json
Get-Content projects/04-urban-mobility-analytics/data/silver/state/silver_state.json
```

Inspect partitioned outputs:

```powershell
Get-ChildItem -Recurse projects/04-urban-mobility-analytics/data/silver/tables/trips
Get-ChildItem -Recurse projects/04-urban-mobility-analytics/data/gold/tables
```

Validation expectations:

- state files should show completed source months;
- a rerun without force should show skipped months in latest-run metadata;
- Silver metadata should show row-count preservation and critical timestamp checks;
- Silver and Gold partition paths should be organized by `pickup_year` and `pickup_month`;
- filenames should retain the selected source month, such as `yellow_taxi_trips_2024-01.parquet`.

## Notebook Usage

The validation notebook is intentionally lightweight and should be run with the same environment used for the project jobs.

Supported launch locations:

- repository root;
- `projects/04-urban-mobility-analytics/`;
- `projects/04-urban-mobility-analytics/notebooks/`.

The notebook bootstraps `src/` automatically from those locations and raises a clear `RuntimeError` when launched from somewhere else.

Before opening the notebook, land at least one source month:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_ingestion.py --start-month 2024-01 --end-month 2024-01
```

The notebook then validates:

- raw file presence;
- sample schema and preview rows;
- row count and selected columns;
- pickup and dropoff timestamp bounds;
- null counts for selected fields;
- source-month timestamp spillover in the official raw file.

## Documentation

- [Documentation index](docs/README.md)
- [Source notes](docs/source.md)
- [Bronze layer](docs/bronze.md)
- [Silver layer](docs/silver.md)
- [Gold layer](docs/gold.md)
- [Orchestration](docs/orchestration.md)
- [Incremental model](docs/incremental.md)
- [Operational review guide](docs/operational-review.md)
- [Data layout](data/README.md)

## Known Limitations / Operational Notes

- The project does not yet include Taxi Zone enrichment.
- The current scope focuses on Yellow Taxi only.
- Quality checks are lightweight and metadata-oriented, not a full assertion framework.
- The pipeline is local-first and not optimized for very large historical backfills.
- Prefect is used as a local orchestration surface, not a deployed scheduler.
- There is no serving layer, DBT layer, dashboard, or API in this phase.
- The notebook is a validation surface, not a reusable transformation layer.
- Historical TLC files can include pickup timestamp spillover outside the nominal source month. The pipeline records and partitions this behavior instead of filtering it away.

## Future Directions

- add Taxi Zone lookup enrichment;
- add stronger data quality assertions and anomaly checks;
- add DBT marts over the Silver and Gold outputs when that modeling layer becomes the next proof point;
- add scheduled orchestration and observability later if the portfolio case needs it;
- add a serving or visualization layer only if a later phase clearly benefits from it.
