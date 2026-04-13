# Serving Layer - PostgreSQL

The serving stage loads the Pandas-based Gold CSV outputs into local PostgreSQL
and creates lightweight views for future API and dashboard consumption.

PostgreSQL is used at this stage because the project already has local database
connectivity and the Gold outputs are small, curated datasets. This keeps the
serving layer realistic without adding Flask, dashboard code, Spark, DBT, or
deployment infrastructure before they are needed.

## Schemas

### `analytics`

The `analytics` schema stores physical tables loaded from Gold CSV artifacts.
These tables are the database copy of the current Gold layer.

### `serving`

The `serving` schema exposes stable, lightweight views over the analytics
tables. Future API endpoints and dashboard queries should read from these views
instead of reaching back to local CSV files or earlier medallion layers.

## Loaded Gold Outputs

The serving job reads the existing Gold artifacts from:

```text
projects/01-hospital-analytics/data/gold/
```

It loads:

- `daily_patient_flow.csv` into `analytics.daily_patient_flow`
- `department_referral_summary.csv` into `analytics.department_referral_summary`
- `demographic_summary.csv` into `analytics.demographic_summary`

The loader creates the tables if they do not exist, truncates their contents on
each run, and reloads the CSV data. This is a pragmatic local-development
strategy that keeps repeated runs deterministic while the project is still
small.

## Serving Views

The job creates or replaces:

- `serving.v_daily_patient_flow`
- `serving.v_department_referral_summary`
- `serving.v_demographic_summary`
- `serving.v_dashboard_kpis`

The first three views expose the corresponding analytics tables directly.

`serving.v_dashboard_kpis` is a compact one-row summary for future dashboard
cards. It includes:

- `total_patient_events`
- `average_waittime_overall`
- `average_satisfaction_overall`
- `number_of_daily_points`
- `number_of_department_groups`
- `number_of_demographic_groups`

The KPI view uses simple weighted calculations from the Gold aggregates. It is a
serving convenience view, not a new source of clinical or operational business
meaning.

## How to Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/src/jobs/run_serving.py
```

If your virtual environment is already activated:

```powershell
python projects/01-hospital-analytics/src/jobs/run_serving.py
```

The job uses the existing PostgreSQL connection utility and loads credentials
from:

```text
projects/01-hospital-analytics/.env
```

Expected output includes the target schemas, loaded tables, row counts, and
created views.

## Validation

The serving job performs light validation:

- Gold CSV files must exist.
- Gold CSV files must not be empty.
- Loaded PostgreSQL row counts must match CSV row counts.
- View creation must complete successfully.

## Out of Scope

This stage does not:

- Rebuild Gold logic.
- Read from Bronze or Silver for serving.
- Use Spark.
- Add Flask API endpoints.
- Build dashboard code.
- Introduce DBT models.
- Add deployment or infrastructure tooling.
