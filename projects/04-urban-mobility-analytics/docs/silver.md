# Silver Layer

## Purpose

Silver standardizes Yellow Taxi trip records while preserving trip-level row grain.

This is still a detail-preserving layer, not an aggregated serving model.

## Silver Output

```text
data/silver/tables/trips/pickup_year=YYYY/pickup_month=MM/yellow_taxi_trips_YYYY-MM.parquet
```

The filename tracks the selected source month. The directory path tracks the resolved pickup partition used for local analytics.

That distinction is intentional:

- source-month planning stays aligned with the official TLC file layout;
- Silver partitioning stays aligned with parsed pickup time;
- metadata records the resulting partition details for each processed source month.

## Standardization Rules

- normalize column names to lowercase snake case;
- rename TLC-style identifiers such as `VendorID`, `RatecodeID`, `PULocationID`, and `DOLocationID`;
- parse pickup and dropoff timestamps safely;
- parse numeric columns safely;
- derive `pickup_date`, `pickup_year`, `pickup_month`, `pickup_day`, `pickup_hour`;
- derive `trip_duration_minutes`;
- retain `source_year`, `source_month`, and `source_month_id` for traceability.

When a record lands outside the selected source month based on its parsed pickup timestamp, the Silver write path follows the resolved pickup partition and the metadata records that anomaly instead of silently hiding it. This is documented as source spillover, not treated as a pipeline defect.

## Quality Checks

Silver metadata captures lightweight validation signals such as:

- row count preservation;
- duplicate full-row count;
- null counts for core analytical columns;
- negative-value counts for selected amount and distance fields;
- pickup timestamps outside the selected source month;
- invalid negative trip durations.

These checks are intentionally inspectable and local-first. They are not framed as a full enterprise data quality platform.
