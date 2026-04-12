# Bronze Layer

## Purpose

Bronze is the raw data foundation for the hospital analytics project. At this stage, the goal is to understand and document what landed locally before applying business logic, cleaning, modeling, or serving patterns.

## Current Implementation

The initial Bronze foundation currently does the following:

- Locates the local raw dataset directory at `data/bronze/raw/healthcare_analytics_patient_flow/`.
- Recursively inventories files found in the raw landing area.
- Filters supported data files for profiling, currently CSV files.
- Selects the main CSV file using a simple deterministic rule: largest CSV by file size, with path-based tie breaking.
- Profiles the selected raw CSV with Pandas.
- Writes a readable JSON metadata artifact under `data/bronze/metadata/`.

The profile captures row count, column count, raw column names, Pandas-inferred data types, null counts by column, and duplicate row count.

## Intentionally Not Done Yet

This Bronze step does not:

- Use PySpark while the local Java/Spark environment is blocked.
- Rename columns.
- Standardize values.
- Clean nulls.
- Deduplicate records.
- Apply Silver transformations or business rules.
- Create Gold metrics.
- Load data into PostgreSQL.
- Build dashboards or API endpoints.

Raw fidelity is preserved so the next phase can make explicit Silver-layer decisions.

## Bronze vs Silver

Bronze records what arrived and captures technical metadata about the raw files. Silver will come later and should be responsible for cleaning, schema decisions, conformance, quality rules, and business-ready intermediate datasets.

## Metadata JSON

The Bronze metadata JSON is an operational and documentation artifact. It records:

- Dataset handle.
- Local raw directory.
- Generation timestamp.
- Discovered files.
- Selected main file.
- Main file selection rule.
- Profiling summary.
- Notes about the current Bronze scope.

This gives the project a reproducible starting point before moving into Silver.

## How to Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/src/jobs/run_bronze.py
```

If your virtual environment is already activated, `python projects/01-hospital-analytics/src/jobs/run_bronze.py` is equivalent.

Expected output is a concise console summary plus a metadata file at:

```text
projects/01-hospital-analytics/data/bronze/metadata/healthcare_analytics_patient_flow_bronze_metadata.json
```
