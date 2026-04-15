# Modeling Design

## Layered Architecture

This project follows the standard dbt three-layer model: staging → intermediate → marts.
Each layer has a distinct responsibility and a clear materialization choice.

```
bigquery-public-data.stackoverflow
          │
          ▼
    ┌──────────────────────────┐
    │       staging (views)    │  stg_stackoverflow__questions
    │                          │  stg_stackoverflow__answers
    │  One model per source    │  stg_stackoverflow__users
    │  table. Year-window      │  stg_stackoverflow__tags
    │  filter applied here.    │
    └──────────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────┐
    │   intermediate (views)   │  int_questions_with_answers
    │                          │  int_question_tag_exploded
    │  Joins, enrichment,      │  int_user_question_activity
    │  derived columns.        │
    │  Not for direct use.     │
    └──────────────┬───────────┘
                   │
                   ▼
    ┌──────────────────────────┐
    │      marts (tables)      │  mart_monthly_question_activity
    │                          │  mart_tag_activity
    │  Final analytical        │  mart_answer_latency
    │  outputs. Materialized   │  mart_question_outcomes
    │  as BigQuery tables.     │  mart_user_reputation_segments
    └──────────────────────────┘
```

---

## Staging Layer

**Materialization:** `view`

Staging models are thin wrappers over the source tables. They:

- Apply the `stackoverflow_min_year` cost-control filter (questions and answers only)
- Rename columns to consistent, analytics-friendly names
- Cast types explicitly (INTEGER, TIMESTAMP, DATE)
- Derive simple convenience columns (e.g., `has_accepted_answer`, `is_unanswered`,
  `reputation_tier`, `created_month_start`)
- Normalize the tag string from `<python><pandas>` to `python|pandas`
- Exclude system user stubs (`id <= 0`) from the users table

No business logic or joins live in staging. Each model references exactly one source table.

**Why views at staging?**
Staging models are cheap SELECT statements with filters. Materializing them as views
means the `stackoverflow_min_year` predicate is always pushed through to the source,
keeping intermediate and mart queries cost-efficient without an additional table write.

---

## Intermediate Layer

**Materialization:** `view`

Intermediate models perform joins, aggregations, and enrichment to prepare
analytics-ready datasets for the marts. They:

- Join questions with answer aggregates and accepted-answer timestamps
  (`int_questions_with_answers`)
- Explode the tag string into one row per (question, tag) pair
  (`int_question_tag_exploded`)
- Summarize per-user question activity and join with user context
  (`int_user_question_activity`)

Intermediate models are not intended for direct querying. They exist to keep
mart SQL readable and to share enrichment logic across multiple marts.

**Why views at intermediate?**
The year-window filter in staging already limits the data volume significantly.
Keeping intermediates as views avoids a redundant mid-layer table write in BigQuery
and means the filter propagates naturally to the final table write at the mart level.

---

## Marts Layer

**Materialization:** `table`

Marts are the final analytical outputs. They are materialized as BigQuery tables so
downstream consumers (notebooks, ad-hoc queries, future BI tools) query pre-aggregated
results without scanning staging views on every access.

| Mart | Grain | Primary use |
|---|---|---|
| `mart_monthly_question_activity` | Calendar month | Volume and resolution trends over time |
| `mart_tag_activity` | Tag | Technology ecosystem health by tag |
| `mart_answer_latency` | Calendar month | Response-time distribution trends |
| `mart_question_outcomes` | Question | Question-level fact for ad-hoc segmentation |
| `mart_user_reputation_segments` | Reputation tier | Experience-level vs. question quality |

---

## Design Decisions

**No body column anywhere.**
The `body` column in posts tables contains HTML text (~50–100 GB extra scan cost).
It is not needed for structured marts and is excluded at staging.

**Accepted-answer join via answer_id, not post lookup.**
The `accepted_answer_id` on a question references a row in `posts_answers`.
The intermediate model resolves this join to get the accepted answer's timestamp,
enabling time-to-resolution calculations without a self-join on posts.

**Tag explosion in intermediate, not staging.**
Exploding tags in staging would multiply the base row count before any aggregation.
Keeping the flat tag string in staging and exploding in intermediate (`int_question_tag_exploded`)
limits the explosion to models that need it.

**approx_quantiles for percentiles.**
BigQuery's `APPROX_QUANTILES` is used for median and percentile calculations in mart
aggregations. Exact quantiles (`PERCENTILE_CONT`) require an analytic window function
and are more expensive. For these marts, approximate quantiles are accurate enough.
