# Operational Review Guide

This guide is for reviewers who want to validate the project as a local orchestration, incremental, and partition-aware batch pipeline.

## Review Path

Start with the flow:

```text
src/orchestration/flows.py
```

Then inspect the state and processing logic:

```text
src/ingestion/state.py
src/ingestion/sources.py
src/processing/silver/pipeline.py
src/processing/gold/pipeline.py
```

Finally inspect the generated artifacts after a local run:

```text
data/bronze/state/
data/bronze/metadata/
data/silver/metadata/
data/gold/metadata/
data/silver/tables/
data/gold/tables/
```

## Windows Local Run

From the repository root:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-01
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-01
```

The first command should process the month. The second command should report skipped months because the state files already mark the selected source month complete.

Force a rebuild when you want to verify overwrite behavior:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_flow.ps1 -StartMonth 2024-01 -EndMonth 2024-01 -Force
```

## What Latest-Run Metadata Shows

Each latest-run metadata file includes:

- `status`
- `run_started_at_utc`
- `run_completed_at_utc`
- `selected_month_window`
- `selected_months`
- `processed_months`
- `skipped_months`
- `processed_month_count`
- `skipped_month_count`
- `force`
- `output_paths`
- `state_path`
- layer-specific results

This keeps operational review local and lightweight while still making rerun behavior visible.

## Incremental Behavior To Validate

State is keyed by source month. For example, the official file `yellow_tripdata_2024-01.parquet` maps to source month `2024-01`.

Normal reruns:

- read each layer state file;
- skip selected months already marked `completed`;
- return a skipped result in latest-run metadata;
- leave existing output files in place.

Forced reruns:

- process every selected source month;
- redownload or rebuild layer outputs for that selected window;
- clear Silver and Gold files for the selected source month before writing replacements;
- update the state entry and latest-run metadata.

## Partition Behavior To Validate

Bronze is organized by source month:

```text
data/bronze/raw/yellow_taxi/year=2024/month=01/source.parquet
```

Silver and Gold are organized by resolved pickup month:

```text
data/silver/tables/trips/pickup_year=2024/pickup_month=01/yellow_taxi_trips_2024-01.parquet
data/gold/tables/daily_trip_summary/pickup_year=2024/pickup_month=01/daily_trip_summary_2024-01.parquet
```

The directory partition answers "when did the trip occur by pickup timestamp?" The filename answers "which official source month produced this file?"

Official TLC files can include records whose pickup timestamp spills into a neighboring month. The pipeline records that as source behavior and writes those records to the resolved pickup partition while preserving the source-month filename.

## Data Quality Surface

Silver month metadata is the main validation surface. Inspect:

```text
data/silver/metadata/silver_month_YYYY-MM.json
```

The quality report includes:

- expected core columns present;
- row-count preservation from raw to Silver;
- critical pickup and dropoff timestamp null counts;
- invalid duration count for `dropoff_datetime < pickup_datetime`;
- non-negative monetary and distance checks;
- pickup timestamp spillover count;
- expected partition columns present.

The checks are intentionally metadata-oriented and reviewer-friendly. They are not a replacement for a production data-quality service.

## Portfolio Evidence

Useful lightweight screenshots for a portfolio review:

- Prefect local flow run in the terminal;
- `latest_silver_run.json` showing processed and skipped months;
- `silver_state.json` showing completed source months;
- recursive listing of partitioned Silver or Gold output folders;
- notebook cells validating raw schema and timestamp spillover.
