# Cost-Aware Query Design

BigQuery charges primarily by bytes scanned. The Stack Overflow public dataset is large enough that
careless queries can cost real money during normal development. This document explains the choices
that keep the project practical, reviewable, and honest as a warehouse-first case study.

## Reviewer Takeaway

Cost awareness is part of the modeling design:

- constrain source scans with a year-window variable;
- exclude large HTML text columns that the marts do not need;
- keep staging and intermediate models as views;
- persist only the final marts as BigQuery tables;
- use approximate percentile functions where exact percentiles are not required;
- run narrower development windows before running the full default build.

## Source Table Sizes

Approximate unfiltered sizes:

| Table | Estimated size |
|---|---|
| `posts_questions` | 60-70 GB |
| `posts_answers` | 70-80 GB |
| `users` | 2 GB |
| `tags` | < 10 MB |

A full scan across questions and answers alone can read about 140 GB. At BigQuery on-demand pricing,
that is roughly $0.88 for one careless query. Repeating that during development is the risk this
project avoids.

## Decision 1: Year-Window Filter In Staging

Both `stg_stackoverflow__questions` and `stg_stackoverflow__answers` apply:

```sql
where extract(year from creation_date) >= {{ var('stackoverflow_min_year') }}
```

Default: `stackoverflow_min_year = 2021`.

This reduces the effective scan from roughly 140 GB to about 15-20 GB across the large posts tables.
The filter is variable-driven so reviewers can run cheaper development windows:

```bash
dbt run --vars '{"stackoverflow_min_year": 2023}'
```

PowerShell wrapper:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -MinYear 2023
```

Use a narrow window while editing SQL. Use the default 2021 window for the full portfolio build.

## Decision 2: Large Text Columns Are Excluded

The Stack Overflow posts tables include large HTML `body` columns. They are intentionally never
selected in staging because the current marts answer structured analytics questions and do not need
raw text.

Because BigQuery is columnar, excluding `body` avoids scanning tens of extra gigabytes on every run.
This is a simple but important warehouse-native optimization.

## Decision 3: Staging And Intermediate Are Views

Staging and intermediate models materialize as views.

Why:

- no redundant table writes while developing;
- the year-window predicate remains visible in the compiled query path;
- intermediate transformation logic stays documented without creating extra persisted copies;
- marts are the intended query surface.

Trade-off: repeated ad-hoc queries against intermediate views may re-scan upstream data. That is
acceptable here because reviewers and downstream consumers should inspect the mart tables.

## Decision 4: Marts Are Tables

Mart models materialize as BigQuery tables.

Why:

- the expensive source scan happens during model build;
- downstream reads hit pre-aggregated tables;
- mart outputs are stable and easy to inspect in BigQuery;
- dbt docs can describe the final analytical contract cleanly.

## Decision 5: Approximate Quantiles

`APPROX_QUANTILES` is used for latency percentiles instead of exact analytic percentile functions.
For monthly response-time trend analysis, approximate percentiles are accurate enough and cheaper to
compute.

## Decision 6: Tag Explosion Is Scoped

Tags are exploded from the pipe-delimited string only in `int_question_tag_exploded`. Models that do
not need tag-level rows never reference the exploded intermediate, avoiding unnecessary row
multiplication.

## Decision 7: Minimum Tag Threshold

`mart_tag_activity` keeps only tags with at least 10 questions in the selected window:

```sql
having count(distinct question_id) >= 10
```

This keeps the mart focused on meaningful tags and avoids filling the output with low-signal rows.

## Cost Summary

| Layer | Materialization | Cost behavior |
|---|---|---|
| Staging | View | No persisted write; filters large source tables |
| Intermediate | View | No persisted write; prepares reusable logic |
| Marts | Table | Scans filtered view graph once and persists reviewable outputs |

Estimated default full `dbt run`: 15-20 GB scanned, or roughly $0.09-$0.13 at on-demand pricing.

Cheaper development loop:

```bash
dbt run --select +mart_monthly_question_activity --vars '{"stackoverflow_min_year": 2023}'
dbt test --select mart_monthly_question_activity
```

PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -Select "+mart_monthly_question_activity" -MinYear 2023
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1 -Select mart_monthly_question_activity
```

## What This Project Does Not Do

- It does not configure budget alerts. A production deployment should.
- It does not partition or cluster mart tables. The marts are small after aggregation.
- It does not use BI Engine or BigQuery materialized views.
- It does not model raw HTML body text or NLP features.
- It does not claim production scheduling or warehouse operations.
