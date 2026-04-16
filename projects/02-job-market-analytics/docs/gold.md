# Gold Layer

Gold v1 creates curated analytical summaries from the Silver dataset.

## Current Outputs

Gold writes these local CSV artifacts under `data/gold/`:

- `job_title_summary.csv`
- `industry_summary.csv`
- `location_summary.csv`
- `automation_ai_summary.csv`
- `gold_metadata.json`

## Output Grains

- `job_title_summary`: one row per `job_title`.
- `industry_summary`: one row per `industry`.
- `location_summary`: one row per `location`.
- `automation_ai_summary`: one row per `automation_risk` and `ai_adoption_level` combination.

## Metrics

The summary outputs use explicit, source-supported metrics:

- `total_records`: number of Silver records in the group.
- `average_salary_usd`: average numeric salary, ignoring nulls.
- `median_salary_usd`: median numeric salary, ignoring nulls.
- `min_salary_usd`: minimum salary where included.
- `max_salary_usd`: maximum salary where included.
- `remote_friendly_share`: share of records where `remote_friendly = 'yes'`.
- `high_automation_risk_share`: share of records where `automation_risk = 'high'`.
- `high_ai_adoption_share`: share of records where `ai_adoption_level = 'high'`.
- `growth_projection_share`: share of records where `job_growth_projection = 'growth'`.

Gold does not convert `job_growth_projection` into a numeric score because the Silver field is categorical.

## Run Command

From the repository root:

```powershell
python projects/02-job-market-analytics/src/jobs/run_gold.py
```

If the Silver artifact is missing, run:

```powershell
python projects/02-job-market-analytics/src/jobs/run_silver.py
```

## Current Limitations

- Gold v1 is implemented in Pandas, not DBT.
- Gold v1 is local-file based and does not publish to PostgreSQL.
- The API and dashboard consume PostgreSQL dbt marts, not these local Gold CSV files.
- The outputs are analytical summaries, not production-certified marts.

## dbt Relationship

The Gold outputs are intentionally named and grained like the dbt marts. They remain useful as local medallion artifacts, while the dbt project is now the stronger SQL review surface.

The implemented dbt marts formalize similar analytical grains with SQL models, model documentation, and tests for categorical values, share ranges, salary ranges, and positive grouped row counts.
