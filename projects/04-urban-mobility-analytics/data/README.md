# Data Layout

This project keeps generated artifacts local, readable, and partition-aware.

## Directory Layout

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
    |   |-- daily_trip_summary/
    |   |-- hourly_trip_summary/
    |   |-- payment_type_summary/
    |   |-- trip_distance_summary/
    |   `-- fare_amount_summary/
    |-- metadata/
    `-- state/
```

## Notes

- raw, Silver, and Gold table artifacts are written as Parquet;
- metadata and state artifacts are written as readable JSON;
- generated runtime artifacts are intentionally local and ignored by Git;
- the repository tracks only this layout documentation, not the generated data.
