# Project 06 — Warehouse-First Analytics

**Stack Overflow Developer Ecosystem | dbt + BigQuery**

---

## Why This Project Exists

The first five portfolio cases prove local-first analytics delivery:

| Project | Key proof point |
|---|---|
| 01 Hospital Analytics | Bronze/Silver/Gold, PostgreSQL, Flask API, React dashboard |
| 02 Job Market Analytics | Python medallion, dbt DuckDB + PostgreSQL, marts, API, dashboard |
| 03 Retail Revenue Analytics | Multi-table sources, dimensional marts, dbt DuckDB, Docker demo |
| 04 Urban Mobility Analytics | Public-source ingestion, incremental Parquet, Prefect orchestration |
| 05 Event Stream Analytics | Broker-based event ingestion, checkpointing, local event-driven architecture |

Project 06 proves something different: **warehouse-first analytics engineering**.

There is no local ingestion pipeline. There is no local data store. There is no
dashboard. There is no API. The entire analytics workflow happens inside BigQuery,
driven by dbt, against a public dataset that is already warehouse-native.

This reflects how a significant portion of real-world analytics engineering works:
the data is already in the warehouse; the job is to model it well.

---

## What This Project Is

- A **dbt BigQuery** project modeling the Stack Overflow public dataset
- A demonstration of **staged analytics engineering**: staging → intermediate → marts
- A case in **cost-aware query design** for a managed cloud warehouse
- A portfolio case with **dbt tests and documentation** as first-class outputs
- A **cloud-warehouse-oriented workflow** that does not pretend to be a production platform

## What This Project Is Not

- Not a dashboard-led project
- Not an API-led project
- Not a local data pipeline
- Not a production deployment claim

---

## Source

**BigQuery public dataset:** `bigquery-public-data.stackoverflow`

Stack Overflow's complete Q&A history (2008–present) is available as a native BigQuery
public dataset. This makes it the ideal source for a warehouse-first case: no ingestion,
no file downloads, no local storage — just SQL modeling directly against the warehouse.

Tables used:

| Table | Rows (approx.) | Size (approx.) |
|---|---|---|
| `posts_questions` | ~24 M | ~65 GB |
| `posts_answers` | ~55 M | ~75 GB |
| `users` | ~21 M | ~2 GB |
| `tags` | ~65 K | < 10 MB |

**Cost control:** All queries in this project apply a `creation_date` year filter
(default: 2021–present). This reduces the effective scan volume to ~15–20 GB per
full `dbt run`, bringing per-run cost to approximately **$0.09–$0.13** at on-demand
BigQuery pricing. See [docs/cost-awareness.md](docs/cost-awareness.md).

---

## What BigQuery Contributes

- **Native source access:** The dataset is already in BigQuery. No ingestion step.
- **Columnar storage:** Only referenced columns are scanned; the `body` column
  (~50–100 GB) is never touched.
- **Serverless execution:** No cluster management or local compute.
- **Managed storage for marts:** Materialized tables persist without infrastructure.
- **approx_quantiles:** Native probabilistic aggregates for latency percentiles.

---

## What dbt Contributes

- **Layered modeling:** staging → intermediate → marts, each with a clear contract
- **Source documentation:** Column descriptions, caveats, and grains in YAML
- **Schema tests:** not_null, unique, accepted_values across all layers
- **Singular tests:** Custom SQL assertions for business invariants
- **Variable-driven config:** `stackoverflow_min_year` controls the cost window
- **Materialization strategy:** views at staging/intermediate, tables at marts

---

## dbt Project Structure

```
dbt/
├── dbt_project.yml
├── profiles.yml.example
├── packages.yml               (dbt_utils)
├── requirements.txt
├── scripts/
│   └── run_dbt_bigquery.sh   (debug → deps → run → test)
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── _staging_models.yml
│   │   ├── stg_stackoverflow__questions.sql
│   │   ├── stg_stackoverflow__answers.sql
│   │   ├── stg_stackoverflow__users.sql
│   │   └── stg_stackoverflow__tags.sql
│   ├── intermediate/
│   │   ├── _intermediate_models.yml
│   │   ├── int_questions_with_answers.sql
│   │   ├── int_question_tag_exploded.sql
│   │   └── int_user_question_activity.sql
│   └── marts/
│       ├── _marts_models.yml
│       ├── mart_monthly_question_activity.sql
│       ├── mart_tag_activity.sql
│       ├── mart_answer_latency.sql
│       ├── mart_question_outcomes.sql
│       └── mart_user_reputation_segments.sql
└── tests/
    ├── assert_answer_latency_non_negative.sql
    ├── assert_mart_monthly_positive_counts.sql
    ├── assert_tag_activity_min_question_count.sql
    └── assert_reputation_tier_coverage.sql
```

---

## Marts

| Mart | Grain | What it answers |
|---|---|---|
| `mart_monthly_question_activity` | Calendar month | Volume, resolution rates, and response time trends |
| `mart_tag_activity` | Tag | Technology ecosystem health by tag |
| `mart_answer_latency` | Calendar month | Response-time distributions (p25/p50/p75/p90) |
| `mart_question_outcomes` | Question | Per-question outcome and score classification |
| `mart_user_reputation_segments` | Reputation tier | How experience level relates to question quality |

Full column reference: [docs/marts.md](docs/marts.md)

---

## Modeling Architecture

```
bigquery-public-data.stackoverflow
          │
          ▼  (year-window filter)
    staging (views)
          │
          ▼  (joins, enrichment)
    intermediate (views)
          │
          ▼  (aggregations)
    marts (BigQuery tables)
```

Staging and intermediate models materialize as `VIEW` — the year-window predicate
propagates to the source and is evaluated once at mart build time. Marts materialize
as `TABLE` so downstream consumers query pre-aggregated results cheaply.

See [docs/modeling.md](docs/modeling.md) for full design rationale.

---

## How to Run Locally

### Quick start

```bash
# 1. Python environment
python -m venv .venv && source .venv/bin/activate
pip install -r dbt/requirements.txt

# 2. Authenticate
gcloud auth application-default login

# 3. Configure dbt profile
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml — set your GCP project ID

# 4. Run everything
cd dbt/
bash scripts/run_dbt_bigquery.sh
```

### Individual commands

```bash
cd dbt/
dbt debug                                           # validate connection
dbt deps                                            # install packages
dbt run                                             # build all models
dbt test                                            # run all tests
dbt run --select staging                            # staging only
dbt run --select +mart_monthly_question_activity    # mart + upstream
dbt docs generate && dbt docs serve                 # browse documentation
```

### Reduce cost during development

```bash
# Limit to 2023-present (fewer bytes scanned)
dbt run --vars '{"stackoverflow_min_year": 2023}'
```

Full guide: [docs/local-run.md](docs/local-run.md)

---

## Cost Awareness

| Decision | Effect |
|---|---|
| Year-window filter in staging (default: 2021+) | ~85–90% scan reduction vs. full table |
| Views at staging/intermediate | Predicate propagates to source; no redundant table writes |
| Tables at marts | Pre-aggregated; downstream reads are cheap |
| Body column excluded | ~50–100 GB scan avoided on every run |
| approx_quantiles for percentiles | Cheaper than PERCENTILE_CONT analytic functions |
| Tag explosion in intermediate only | Avoids row multiplication in staging views |

Estimated cost per full `dbt run` with default settings: **$0.09–$0.13**

See [docs/cost-awareness.md](docs/cost-awareness.md).

---

## Current Limitations

- **Year window:** Default covers 2021–present. Pre-2021 history is excluded by design
  for cost control. The full historical dataset is available by adjusting the variable.

- **No freshness checks:** The public dataset refreshes are not on a documented schedule.
  dbt source freshness tests are not included in v1.

- **No body/text analysis:** Question and answer HTML bodies are excluded. NLP features
  (topic modeling, sentiment) would require a separate enrichment pipeline.

- **Accepted answer window mismatch:** `accepted_answer_id` on a question may reference
  an answer created before `stackoverflow_min_year`. In that case the accepted answer
  will not appear in the answers staging view and the join resolves to NULL.

- **Not a production deployment:** No warehouse scheduling, no CI/CD, no alerting,
  no budget caps. This is a local analytics engineering demonstration.

---

## Future Directions

- Monthly incremental builds to reduce per-run cost further
- dbt exposures to document downstream consumers
- Source freshness monitoring once a refresh schedule is known
- Additional marts: `mart_monthly_tag_trends`, `mart_user_answer_quality`
- Observability: dbt artifacts analysis, model run time tracking
- Serving layer: if a presentation layer is later justified, mart tables can be
  queried directly by Looker Studio or similar without modification

---

## Documentation

| Document | Contents |
|---|---|
| [docs/source.md](docs/source.md) | Source inspection, table schemas, caveats |
| [docs/modeling.md](docs/modeling.md) | Layer design, materialization decisions |
| [docs/marts.md](docs/marts.md) | Mart reference: grain, columns, example queries |
| [docs/tests.md](docs/tests.md) | Test inventory and rationale |
| [docs/cost-awareness.md](docs/cost-awareness.md) | All cost-control decisions explained |
| [docs/local-run.md](docs/local-run.md) | Step-by-step setup and run instructions |
| [notebooks/README.md](notebooks/README.md) | Source validation notebook guide |
