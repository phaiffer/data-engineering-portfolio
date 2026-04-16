# PostgreSQL Mart Inspection

Use this guide after running the PostgreSQL dbt path.

## Expected Tables

```text
analytics.job_market_insights_silver
marts.mart_job_title_summary
marts.mart_industry_summary
marts.mart_location_summary
marts.mart_automation_ai_summary
```

The `analytics` table is the loaded Silver source. The `marts` tables are dbt outputs used by the API and dashboard.

## Existence and Row Counts

```sql
select table_schema, table_name
from information_schema.tables
where table_schema in ('analytics', 'marts')
order by table_schema, table_name;

select count(*) from analytics.job_market_insights_silver;
select count(*) from marts.mart_job_title_summary;
select count(*) from marts.mart_industry_summary;
select count(*) from marts.mart_location_summary;
select count(*) from marts.mart_automation_ai_summary;
```

## Mart Review Queries

Highest-paying job-title summaries:

```sql
select
    job_title,
    total_records,
    average_salary_usd,
    remote_friendly_share,
    high_ai_adoption_share
from marts.mart_job_title_summary
order by average_salary_usd desc
limit 10;
```

Industry risk and AI adoption:

```sql
select
    industry,
    total_records,
    average_salary_usd,
    high_automation_risk_share,
    high_ai_adoption_share
from marts.mart_industry_summary
order by total_records desc
limit 10;
```

Location comparison:

```sql
select
    location,
    total_records,
    average_salary_usd,
    remote_friendly_share
from marts.mart_location_summary
order by average_salary_usd desc
limit 10;
```

Automation and AI matrix:

```sql
select
    automation_risk,
    ai_adoption_level,
    total_records,
    average_salary_usd,
    growth_projection_share
from marts.mart_automation_ai_summary
order by total_records desc;
```

## What To Look For

- Mart row counts should be positive after dbt run.
- Share metrics should stay between `0` and `1`.
- Salary metrics should be positive and within a plausible range for the dataset.
- API endpoint ordering should line up with the corresponding mart queries.

The dbt singular tests cover these assumptions at a lightweight portfolio-review level.
