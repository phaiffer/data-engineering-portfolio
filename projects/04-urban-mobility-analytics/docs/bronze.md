# Bronze Layer

## Purpose

Bronze in this project is the raw month-based landing area plus the raw inventory metadata built over it.

It does not apply business transformations.

## Raw Layout

```text
data/bronze/raw/yellow_taxi/year=YYYY/month=MM/source.parquet
```

Each landed file remains close to the official source artifact.

## What Bronze Does

- plans official source months;
- downloads the selected monthly Parquet files;
- stores them in a local partition-aware layout;
- tracks landed months in `data/bronze/state/ingestion_state.json`;
- profiles landed files into Bronze metadata artifacts;
- writes month-level and latest-run metadata under `data/bronze/metadata/`.

## What Bronze Does Not Do

- standardize business column names;
- parse and recast the dataset into analytical types;
- aggregate trips;
- enrich Taxi Zone dimensions.

## Metadata Surface

Bronze metadata includes:

- row count;
- column count;
- schema snapshot;
- file size;
- temporal bounds for pickup and dropoff timestamps when present;
- references back to the ingestion state entry.
