# Source Selection

## Selected Source

This project uses the official NYC Taxi and Limousine Commission Trip Record Data for Yellow Taxi trips.

- TLC trip record page: `https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page`
- Yellow Taxi data dictionary: `https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf`
- Monthly file pattern used by this project: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_YYYY-MM.parquet`

This is intentionally not a Kaggle mirror. The goal is to use a public source that is widely recognized and directly associated with the publishing agency.

## Why It Fits This Case

The NYC TLC dataset is a strong match for this portfolio phase because it naturally supports:

- month-based batch ingestion;
- reproducible local downloads;
- incremental extension one month at a time;
- realistic trip-level operational analysis;
- partitioned Parquet layouts;
- orchestration around a public analytical source.

## Monthly Organization

The Yellow Taxi files are published as one Parquet file per month:

```text
yellow_tripdata_YYYY-MM.parquet
```

That file organization maps well to a local incremental model:

- one selected month becomes one planning unit;
- one month lands into one Bronze raw partition;
- Silver and Gold can safely rerun only the selected months.

The selected month is the source-planning unit, not a guarantee that every trip record inside the file has a pickup timestamp inside that same month.

## Important Columns Used In This Project

The current implementation focuses on documented fields that are stable and analytically useful:

- `VendorID`
- `tpep_pickup_datetime`
- `tpep_dropoff_datetime`
- `passenger_count`
- `trip_distance`
- `RatecodeID`
- `store_and_fwd_flag`
- `PULocationID`
- `DOLocationID`
- `payment_type`
- `fare_amount`
- `extra`
- `mta_tax`
- `tip_amount`
- `tolls_amount`
- `improvement_surcharge`
- `total_amount`
- `congestion_surcharge`
- `airport_fee`
- `cbd_congestion_fee` when present in newer files

## Important Caveats

- TLC monthly files can be large, so this project keeps the default window small.
- Schema details can evolve over time. The implementation handles optional numeric columns such as `cbd_congestion_fee` when they appear.
- This phase does not yet join Taxi Zone lookup metadata, so location analysis stays at the numeric location ID level.
- A monthly TLC file can contain a small number of records whose parsed pickup timestamp falls outside the nominal source month.
- The pipeline treats that as a source-data characteristic: ingestion still tracks the file by source month, while Silver and Gold partition downstream outputs by resolved pickup year and month.
- Spillover rows are visible in metadata and notebook validation rather than being silently filtered away.

## Why The Default Window Is Small

The default month window is intentionally limited to `2024-01` through `2024-02`.

That keeps the first local run practical while still proving:

- official-source ingestion;
- incremental month tracking;
- partition-aware processing;
- orchestrated local reruns.
