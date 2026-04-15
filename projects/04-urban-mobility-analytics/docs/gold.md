# Gold Layer

## Purpose

Gold in this phase produces operational summaries that are useful for local analytical review without pretending to be a final serving mart.

## Current Outputs

- `daily_trip_summary`
- `hourly_trip_summary`
- `payment_type_summary`
- `trip_distance_summary`
- `fare_amount_summary`

## Metric Surface

The current summaries use fields directly supported by the source and standardized Silver table:

- `trip_count`
- `passenger_count_sum`
- `total_fare_amount`
- `total_tip_amount`
- `total_tolls_amount`
- `average_trip_distance`
- `average_total_amount`
- `average_fare_amount`

## Output Layout

Each Gold table is partitioned by pickup year and month:

```text
data/gold/tables/<table_name>/pickup_year=YYYY/pickup_month=MM/<table_name>_YYYY-MM.parquet
```

As in Silver, the filename retains the selected source month while the directory reflects the resolved pickup partition. A single source-month file can therefore produce a few spillover Gold partitions when the official raw file contains out-of-month pickup timestamps.

## Modeling Notes

- Gold reads the partitioned Silver Parquet outputs with DuckDB.
- The summaries are month-rerunnable and local-first.
- Gold inherits the Silver partition semantics instead of forcing all records back into the nominal source month.
- This phase avoids zone enrichment, dashboard-driven marts, and a public serving contract.
