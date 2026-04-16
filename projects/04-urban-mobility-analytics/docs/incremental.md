# Incremental Model

## What Incremental Means Here

Incremental in this project means processing the pipeline month by month with readable local state tracking.

The selected month window is the core unit of rerun behavior.

## State Files

- `data/bronze/state/ingestion_state.json`
- `data/bronze/state/bronze_state.json`
- `data/silver/state/silver_state.json`
- `data/gold/state/gold_state.json`

Each state file records completed source months and lightweight run details.

Those state files are keyed by source month because the official TLC publication pattern is month-based.

Latest-run metadata is written separately under each layer metadata directory. These files are optimized for quick operational review and include the selected month window, processed months, skipped months, run timestamps, output paths, status, and the state file path updated by the run.

## Default Behavior

When a month is already marked complete in a layer state file:

- reruns skip it by default;
- the state remains readable and inspectable;
- later months can still be added without rebuilding everything.

This remains true even if the processed month writes a few Silver or Gold partitions outside the nominal source month because of parsed pickup-time spillover in the raw data.

## Forced Rebuilds

Use `--force` to rebuild the selected month window:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_silver.py --start-month 2024-02 --end-month 2024-02 --force
```

On Windows PowerShell, the helper scripts expose the same behavior:

```powershell
.\projects\04-urban-mobility-analytics\scripts\run_silver.ps1 -StartMonth 2024-02 -EndMonth 2024-02 -Force
```

That keeps the incremental model simple and honest:

- skip already-completed months when nothing changed;
- allow explicit rebuilds when you want them;
- avoid claiming a more advanced CDC or watermark framework than the project actually implements.

## Layer-by-Layer Behavior

- Ingestion tracks landed raw months.
- Bronze tracks profiled raw months.
- Silver tracks standardized months and rewrites only those month outputs when forced.
- Gold tracks aggregated months and rewrites only those month outputs when forced.

Silver and Gold still partition outputs by resolved pickup year and month, so source-month state tracking and downstream pickup partitions intentionally describe different aspects of the same run.

## Duplication Avoidance

Normal reruns avoid duplicate work by checking whether the selected source month is already marked `completed` in the relevant layer state file.

Forced reruns avoid duplicate files differently:

- ingestion removes the selected raw source file before redownloading it;
- Silver removes existing files whose filename matches the selected source month before rewriting partitioned outputs;
- Gold removes existing table files whose filename matches the selected source month before rewriting partitioned outputs.

This means a forced rebuild for `2024-02` replaces files such as `yellow_taxi_trips_2024-02.parquet` without touching files produced by `2024-01` or `2024-03`.

## Source Month Versus Pickup Month

The selected month window follows the official source file name. For example, `2024-02` maps to:

```text
yellow_tripdata_2024-02.parquet
```

Silver and Gold partitions follow parsed pickup timestamps. If a row inside the February source file has a pickup timestamp in January or March, it is written under the resolved pickup partition. The filename still includes `2024-02` so the lineage to the official source month remains visible.

## Why This Fits The Case

This model supports:

- reproducible local execution;
- inspectable manifests;
- partition-aware storage;
- a stronger data pipeline operations story than the earlier portfolio cases.
