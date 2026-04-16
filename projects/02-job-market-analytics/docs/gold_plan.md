# Gold v1 Plan

Gold v1 turns the standardized Silver dataset into small, curated analytical outputs. These outputs are mart-like local CSVs for portfolio review and for comparison with the implemented dbt marts.

## Source

Gold reads only the Silver artifact:

```text
data/silver/ai_job_market_insights_silver.csv
```

It does not read Bronze files directly.

## Output 1: `job_title_summary`

Grain: one row per `job_title`.

Purpose: compare job roles by record volume, salary distribution, remote friendliness, automation risk, AI adoption, and growth-label prevalence.

Silver columns used:

- `job_title`
- `salary_usd`
- `remote_friendly`
- `automation_risk`
- `ai_adoption_level`
- `job_growth_projection`

Metrics:

- `total_records`
- `average_salary_usd`
- `median_salary_usd`
- `min_salary_usd`
- `max_salary_usd`
- `remote_friendly_share`
- `high_automation_risk_share`
- `high_ai_adoption_share`
- `growth_projection_share`

## Output 2: `industry_summary`

Grain: one row per `industry`.

Purpose: compare industries by compensation and job-market label patterns.

Silver columns used:

- `industry`
- `salary_usd`
- `remote_friendly`
- `automation_risk`
- `ai_adoption_level`
- `job_growth_projection`

Metrics match `job_title_summary`.

## Output 3: `location_summary`

Grain: one row per `location`.

Purpose: compare location-level salary and work-model patterns.

Silver columns used:

- `location`
- `salary_usd`
- `remote_friendly`
- `job_growth_projection`
- `automation_risk`
- `ai_adoption_level`

Metrics match `job_title_summary`.

## Output 4: `automation_ai_summary`

Grain: one row per `automation_risk` and `ai_adoption_level` combination.

Purpose: provide a compact analytical table for the interaction between automation risk and AI adoption labels.

Silver columns used:

- `automation_risk`
- `ai_adoption_level`
- `salary_usd`
- `remote_friendly`
- `job_growth_projection`

Metrics:

- `total_records`
- `average_salary_usd`
- `median_salary_usd`
- `remote_friendly_share`
- `growth_projection_share`

## Metric Assumptions

- Salary metrics use numeric `salary_usd` and ignore nulls by standard Pandas aggregation behavior.
- Share metrics are calculated only from explicit Silver category values:
  - `remote_friendly_share`: share of records where `remote_friendly = 'yes'`.
  - `high_automation_risk_share`: share of records where `automation_risk = 'high'`.
  - `high_ai_adoption_share`: share of records where `ai_adoption_level = 'high'`.
  - `growth_projection_share`: share of records where `job_growth_projection = 'growth'`.
- No numeric average is assigned to `job_growth_projection` because the source field is categorical.

## Null Handling

- Grouped null keys are preserved with Pandas `dropna=False`.
- Metric denominators use total records in the group.
- Share metrics return null only for empty groups, which should not occur in these grouped outputs.

## Out of Scope

- Gold CSV files are not the serving layer for the API or dashboard.
- Gold v1 itself is not production dbt.
- No deduplication or synthetic primary keys.
- No salary bands, ordinal scoring, or market representativeness claims.

## dbt Relationship

The Gold outputs have explicit grains and deterministic metrics, which made them suitable candidates for dbt marts. The current dbt implementation now models the same review-friendly grains in SQL and adds tests for accepted categorical values, share ranges, salary ranges, and positive grouped row counts.
