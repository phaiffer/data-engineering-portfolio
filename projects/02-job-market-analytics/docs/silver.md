# Silver Layer

Silver v1 standardizes the Bronze-selected job market CSV into a cleaner, row-preserving dataset for Gold outputs and dbt modeling.

## What Silver Does Now

- Reads the selected main CSV from Bronze metadata.
- Renames raw columns to `snake_case`.
- Trims whitespace from string fields.
- Converts blank strings to nulls.
- Safely casts `salary_usd` to numeric.
- Normalizes categorical values to lowercase analytical tokens.
- Preserves row count.
- Writes a Silver CSV and metadata JSON.
- Runs lightweight validation checks.

## What Silver Does Not Do Yet

- It does not aggregate records.
- It does not deduplicate rows.
- It does not create dimensional tables or final marts.
- It does not create serving tables, a Flask API, or a dashboard by itself.
- It does not claim production dbt maturity; it provides the stable source contract used by dbt.

## Output

Silver artifacts are written locally under:

```text
projects/02-job-market-analytics/data/silver/
```

Expected artifacts:

- `ai_job_market_insights_silver.csv`
- `ai_job_market_insights_silver_metadata.json`

These are generated local artifacts and are ignored by Git.

## Run Command

From the repository root:

```powershell
python projects/02-job-market-analytics/src/jobs/run_silver.py
```

If Bronze metadata or raw files are missing, run:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
```

## dbt Relationship

Silver v1 gives dbt staging a stable row-level contract: predictable column names, normalized categorical values, and an explicit numeric salary field.

The dbt project uses this same Silver artifact in two ways:

- DuckDB reads the Silver CSV directly for fast local SQL model validation.
- PostgreSQL reads a loaded copy of the Silver data from `analytics.job_market_insights_silver` for the API/dashboard serving path.

The Silver layer remains row-preserving. Aggregations belong in Python Gold summaries and dbt marts.
