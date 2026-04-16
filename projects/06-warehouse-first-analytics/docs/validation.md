# Validation Guide

This project is validated through dbt and BigQuery, not through a dashboard or API. A reviewer
should be able to confirm the project by checking dbt connectivity, model builds, tests,
documentation artifacts, and a few focused mart queries.

## Recommended Validation Sequence

Run from the repository root on Windows PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_debug.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_deps.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -MinYear 2023
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_docs_generate.ps1
```

The `-MinYear 2023` run is a cheaper development iteration. Use the default project setting
(`2021`) for the full portfolio build.

Equivalent commands from `projects/06-warehouse-first-analytics/dbt/`:

```bash
dbt debug
dbt deps
dbt run --vars '{"stackoverflow_min_year": 2023}'
dbt test
dbt docs generate
```

## What Each Command Proves

| Command | What to verify |
|---|---|
| `dbt debug` | Profile is present, BigQuery adapter loads, credentials work, connection succeeds |
| `dbt deps` | `dbt_utils` installs from `packages.yml` |
| `dbt run` | Staging and intermediate views compile, mart tables build in BigQuery |
| `dbt test` | Schema tests and singular business assertions pass |
| `dbt docs generate` | Model, source, and column documentation can be rendered into dbt docs artifacts |

## BigQuery Datasets To Inspect

The example profile uses `dataset: stackoverflow_analytics`. dbt appends custom schemas from
`dbt_project.yml`, so BigQuery usually contains:

```text
<project>.stackoverflow_analytics_staging
<project>.stackoverflow_analytics_intermediate
<project>.stackoverflow_analytics_marts
```

Staging and intermediate objects should be views. Mart objects should be tables.

## Mart Inspection Queries

Replace `your-project-id` if your dbt profile uses a different GCP project.

### Monthly Volume And Resolution

```sql
select
  month_start,
  total_questions,
  unanswered_rate_pct,
  accepted_answer_rate_pct,
  median_hours_to_first_answer
from `your-project-id.stackoverflow_analytics_marts.mart_monthly_question_activity`
order by month_start desc
limit 12;
```

Use this to validate the monthly mart grain and the main trend metrics.

### Tag Health

```sql
select
  tag_name,
  questions_in_window,
  unanswered_rate_pct,
  accepted_answer_rate_pct,
  total_historical_question_count
from `your-project-id.stackoverflow_analytics_marts.mart_tag_activity`
order by questions_in_window desc
limit 20;
```

Use this to confirm tag-level aggregation, the 10-question threshold, and the distinction between
window-scoped questions and all-time source tag counts.

### Response-Time Distribution

```sql
select
  month_start,
  questions_with_answers,
  p25_hours_to_first_answer,
  median_hours_to_first_answer,
  p75_hours_to_first_answer,
  p90_hours_to_first_answer
from `your-project-id.stackoverflow_analytics_marts.mart_answer_latency`
order by month_start desc
limit 12;
```

Use this to inspect the approximate percentile strategy and the long-tail response-time pattern.

### Outcome Categories

```sql
select
  outcome_category,
  score_tier,
  count(*) as question_count
from `your-project-id.stackoverflow_analytics_marts.mart_question_outcomes`
group by 1, 2
order by question_count desc;
```

Use this to confirm the question-level fact mart and classification fields.

### Reputation Segments

```sql
select
  reputation_tier,
  tier_rank,
  user_count,
  total_questions,
  avg_accepted_answer_rate_pct,
  avg_question_score
from `your-project-id.stackoverflow_analytics_marts.mart_user_reputation_segments`
order by tier_rank;
```

Use this to verify the fixed five-tier reputation grain.

## Test Artifacts To Review

Schema tests live next to model documentation:

```text
dbt/models/staging/_staging_models.yml
dbt/models/intermediate/_intermediate_models.yml
dbt/models/marts/_marts_models.yml
```

Singular tests live in:

```text
dbt/tests/
```

The singular tests are important project artifacts because they encode business expectations that
generic schema tests cannot express, such as non-negative answer latency, positive monthly counts,
tag activity thresholds, and coverage of reputation tiers.

## Screenshot Guidance

Lightweight portfolio screenshots that fit this project:

- `dbt debug` ending with a successful BigQuery connection;
- `dbt run` showing mart models created as tables;
- `dbt test` with schema and singular tests passing;
- `dbt docs generate` completing successfully;
- BigQuery Explorer showing staging/intermediate views and mart tables;
- one or two mart inspection query results from BigQuery.

Avoid screenshots of dashboards or APIs. The story here is warehouse-first analytics engineering:
dbt models, BigQuery objects, tests, docs, and cost-aware SQL.
