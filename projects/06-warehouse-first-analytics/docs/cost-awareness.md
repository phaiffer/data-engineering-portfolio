# Cost-Aware Query Design

BigQuery charges by bytes scanned, not by query count or wall time. The Stack Overflow
public dataset is large enough that careless queries can cost real money. This document
explains the design decisions made to keep this project cost-efficient.

---

## Source Table Sizes (approximate, unfiltered)

| Table | Estimated size |
|---|---|
| `posts_questions` | ~60–70 GB |
| `posts_answers` | ~70–80 GB |
| `users` | ~2 GB |
| `tags` | < 10 MB |

A full-scan query across questions and answers alone could scan ~140 GB, which at
BigQuery on-demand pricing (~$6.25/TB) costs approximately $0.88 per query.
Multiply that by a development cycle of dozens of iterative runs and costs accumulate.

---

## Decision 1: Year-Window Filter in Staging

**What:** Both `stg_stackoverflow__questions` and `stg_stackoverflow__answers` apply:

```sql
WHERE EXTRACT(year FROM creation_date) >= {{ var('stackoverflow_min_year') }}
```

**Default:** `stackoverflow_min_year = 2021` (4-year window: 2021–2024).

**Effect:** Reduces scan from ~140 GB to approximately 15–20 GB across both tables.
Cost reduction: roughly 85–90%.

**Why EXTRACT(year) instead of a literal date?**
The `creation_date` column is not a partition key in this public dataset.
BigQuery cannot push a partition prune. Using `EXTRACT(year)` is functionally
equivalent to `creation_date >= '2021-01-01'` but makes the variable-driven
intent explicit. For a production table with date partitioning, a
`creation_date >= DATE(...)` filter would enable true partition pruning.

**How to override:**
```bash
# More restricted (2-year window, lower cost)
dbt run --vars '{"stackoverflow_min_year": 2023}'

# Full historical window (high cost - avoid in dev)
dbt run --vars '{"stackoverflow_min_year": 2008}'
```

---

## Decision 2: Views at Staging and Intermediate

**What:** Staging and intermediate models materialize as `VIEW`, not `TABLE`.

**Why:** If staging were materialized as a table, every `dbt run` would write the
filtered data to a new table (scanning the source again + storing the result).
Views defer execution to the mart layer, so the year-window predicate is evaluated
exactly once per mart table build, not once per layer.

**Trade-off:** Repeated queries against intermediate views will re-scan staging.
For this portfolio project, marts are the intended query targets, so this is acceptable.
In a production setting with high query frequency, materializing intermediate models
as tables would reduce repeated source scans.

---

## Decision 3: Tables at Marts

**What:** Mart models materialize as `TABLE`.

**Why:** Marts are the intended read layer. Once built, downstream consumers
(notebooks, ad-hoc queries) query the pre-aggregated mart table without triggering
a source re-scan. This is the key cost-saving pattern for serving analytics:
aggregate once at build time, query cheaply at use time.

---

## Decision 4: Body Column Excluded

**What:** The `body` column (raw HTML text) on both posts tables is never selected.

**Why:** In BigQuery, SELECT from a columnar table only reads the columns requested.
Including `body` would add ~50–100 GB to every staging query. Since marts do not
use free text, excluding it is a zero-cost, zero-downside decision.

---

## Decision 5: approx_quantiles for Percentiles

**What:** `APPROX_QUANTILES` is used in latency marts instead of `PERCENTILE_CONT`.

**Why:** `PERCENTILE_CONT` as an analytic function requires a full sort pass over
the data. `APPROX_QUANTILES` uses a probabilistic sketch, which is cheaper and
faster. For trend monitoring at monthly granularity, ~1–2% approximation error
is acceptable.

---

## Decision 6: Tag Explosion Scoped to Intermediate

**What:** Tags are exploded from the pipe-delimited string in `int_question_tag_exploded`,
not in staging.

**Why:** Exploding tags in a staging view would multiply the row count (on average
~2.5 tags per question) before any filtering. By keeping the flat tag string through
staging and intermediate, only the `mart_tag_activity` build reads the exploded model.
Models that don't need tags (`mart_monthly_question_activity`, `mart_answer_latency`)
never reference the exploded intermediate.

---

## Decision 7: Minimum Tag Threshold in mart_tag_activity

**What:** `HAVING count(distinct question_id) >= 10`

**Why:** The tags table has ~65,000 tags. Without a threshold, the mart would contain
65,000 rows of mostly noise (rare tags with 1–2 questions). The 10-question threshold
reduces the mart to the analytically meaningful tags (~5,000–8,000 in a 4-year window)
while keeping the build query lean.

---

## Cost Summary

| Layer | Materialization | Bytes scanned per dbt run |
|---|---|---|
| Staging | VIEW | 0 (deferred) |
| Intermediate | VIEW | 0 (deferred) |
| Marts (5 tables) | TABLE | ~15–20 GB total (year-window filtered) |

A full `dbt run` with default settings scans approximately 15–20 GB total.
At $6.25/TB this is roughly **$0.09–$0.13 per full run** — well within the
BigQuery free tier (1 TB/month free) and negligible for paid tiers.

---

## What This Project Does Not Do (Intentionally)

- **Cluster or partition the mart tables.** The mart tables are small after aggregation
  (monthly or tag-level grain). Partitioning is not necessary and would add complexity.
  For a large-scale production deployment, partitioning mart tables by `month_start`
  would improve query performance for time-range filters.

- **Use BigQuery BI Engine or materialized views.** Out of scope for a v1 portfolio case.

- **Cost tagging or budget alerts.** Real production deployments should configure GCP
  budget alerts. This is not in scope for a local portfolio demonstration.
