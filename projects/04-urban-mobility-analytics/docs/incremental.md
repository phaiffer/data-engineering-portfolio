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

## Default Behavior

When a month is already marked complete in a layer state file:

- reruns skip it by default;
- the state remains readable and inspectable;
- later months can still be added without rebuilding everything.

## Forced Rebuilds

Use `--force` to rebuild the selected month window:

```bash
python projects/04-urban-mobility-analytics/src/jobs/run_silver.py --start-month 2024-02 --end-month 2024-02 --force
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

## Why This Fits The Case

This model supports:

- reproducible local execution;
- inspectable manifests;
- partition-aware storage;
- a stronger data pipeline operations story than the earlier portfolio cases.
