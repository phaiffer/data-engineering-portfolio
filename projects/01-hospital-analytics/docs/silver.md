# Silver Layer - Hospital Analytics

Silver v1 reads the main Bronze patient flow CSV and writes a row-preserving cleaned artifact for downstream modeling work. It standardizes column names, trims string fields, converts blank strings to nulls, applies safe Pandas type casts, creates `patient_admission_timestamp` when date and time parsing is valid, and adds `silver_loaded_at_utc` for lineage.

The current implementation is intentionally Pandas-based because local PySpark is blocked. It does not force Spark, Databricks, or PostgreSQL.

## What Silver does

- Reads `data/bronze/raw/healthcare_analytics_patient_flow/healthcare_analytics_patient_flow_data.csv`
- Renames raw columns to snake_case Silver columns
- Preserves the working grain: 1 row = 1 patient admission / patient flow event record
- Preserves nullable fields such as `department_referral` and `patient_satisfaction_score`
- Keeps ambiguous `Merged` values as `merged_raw_value`
- Writes `data/silver/healthcare_analytics_patient_flow_silver.csv`
- Writes `data/silver/healthcare_analytics_patient_flow_silver_metadata.json`
- Runs lightweight validation checks for columns, row count, duplicates, nulls, and numeric conversions

## What Silver does not do

- Does not drop rows
- Does not deduplicate
- Does not aggregate
- Does not create Gold metrics
- Does not infer the business meaning of `Merged`
- Does not load data into PostgreSQL
- Does not create serving views or dashboards

## Run command

From the repository root:

```powershell
python projects/01-hospital-analytics/src/jobs/run_silver.py
```

If using the local virtual environment directly:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/src/jobs/run_silver.py
```

## Output

Silver CSV:

- `projects/01-hospital-analytics/data/silver/healthcare_analytics_patient_flow_silver.csv`

Silver metadata:

- `projects/01-hospital-analytics/data/silver/healthcare_analytics_patient_flow_silver_metadata.json`

## Open assumptions

- The row grain remains a working assumption until validated with stronger source documentation.
- `merged_raw_value` is intentionally not interpreted yet.
- `patient_waittime` and `patient_satisfaction_score` are typed as numeric, but their exact business semantics should be confirmed before Gold.
