# Project 06 - Warehouse-First Analytics

**Stack Overflow Developer Ecosystem | dbt + BigQuery**

Project 06 is the repository's warehouse-first analytics engineering case study. It models the
BigQuery public Stack Overflow dataset directly in BigQuery using dbt. There is no local ingestion
pipeline, no local database, no API, and no dashboard. The project demonstrates how to build
documented, tested, cost-aware analytical marts when the data already lives in a managed warehouse.

## What To Review First

Start here if you are reviewing the project quickly:

1. [docs/modeling.md](docs/modeling.md) - staging, intermediate, and mart layer design.
2. [docs/cost-awareness.md](docs/cost-awareness.md) - why the SQL is intentionally cost-aware.
3. [docs/marts.md](docs/marts.md) - mart grain, business questions, caveats, and example queries.
4. [docs/tests.md](docs/tests.md) - schema tests and singular tests as review artifacts.
5. [docs/validation.md](docs/validation.md) - practical dbt and BigQuery validation steps.
6. [dbt/models/marts](dbt/models/marts) - final BigQuery table models.

The main dbt assets to inspect are:

```text
dbt/dbt_project.yml
dbt/models/staging/
dbt/models/intermediate/
dbt/models/marts/
dbt/tests/
dbt/profiles.yml.example
```

## Evaluate In 5 Minutes

From the repository root on Windows PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_debug.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_deps.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -MinYear 2023
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_docs_generate.ps1
```

The `-MinYear 2023` run is a cheaper review or development pass. The default project window is
2021-present.

Expected review signal:

- `dbt debug` confirms the BigQuery profile and credentials;
- `dbt deps` installs `dbt_utils`;
- `dbt run` builds staging and intermediate views plus mart tables;
- `dbt test` validates schema tests and custom SQL assertions;
- `dbt docs generate` creates local dbt documentation artifacts in `dbt/target/`.

## Key Warehouse Insights

This project is designed to prove warehouse-first analytics engineering:

- BigQuery public dataset is the source; no ingestion code is needed.
- dbt owns transformation, documentation, tests, and model lineage.
- Staging and intermediate models are views to avoid redundant persisted copies.
- Marts are tables so reviewers and consumers query stable, pre-aggregated outputs.
- A variable-driven year filter keeps source scans bounded.
- Large HTML `body` columns are excluded because the marts do not need raw text.
- Approximate quantiles provide useful latency percentiles at lower warehouse cost.
- Schema tests and singular tests are first-class project artifacts.

## Why This Project Exists

The first five portfolio cases prove local-first analytics delivery:

| Project | Key proof point |
|---|---|
| 01 Hospital Analytics | Bronze/Silver/Gold, PostgreSQL, Flask API, React dashboard |
| 02 Job Market Analytics | Python medallion, dbt DuckDB + PostgreSQL, marts, API, dashboard |
| 03 Retail Revenue Analytics | Multi-table sources, dimensional marts, dbt DuckDB, Docker demo |
| 04 Urban Mobility Analytics | Public-source ingestion, incremental Parquet, Prefect orchestration |
| 05 Event Stream Analytics | Broker-backed event ingestion, checkpoints, local replay |

Project 06 proves a different pattern: analytics engineering where the raw data is already in the
warehouse and the core work is modeling, testing, documenting, and controlling cost.

## What This Project Is

- A dbt BigQuery project over `bigquery-public-data.stackoverflow`
- A staged modeling case: staging -> intermediate -> marts
- A cost-aware managed-warehouse design
- A documentation-driven review artifact
- A portfolio-grade analytics engineering project

## What This Project Is Not

- Not a dashboard-led project
- Not an API-led project
- Not a local ingestion pipeline
- Not a local data warehouse
- Not a production scheduling or deployment claim

## Source

BigQuery public dataset:

```text
bigquery-public-data.stackoverflow
```

Tables used:

| Source table | Approximate role |
|---|---|
| `posts_questions` | Question facts, outcomes, tags, dates, scores |
| `posts_answers` | Answer timing and accepted-answer joins |
| `users` | User reputation and reputation tiers |
| `tags` | Tag reference data and all-time question counts |

The source is a good fit because it is already warehouse-native. The engineering challenge is not
extracting files; it is turning large public warehouse tables into tested analytical marts.

## dbt Project Structure

```text
dbt/
|-- dbt_project.yml
|-- packages.yml
|-- profiles.yml.example
|-- models/
|   |-- staging/
|   |   |-- sources.yml
|   |   |-- _staging_models.yml
|   |   |-- stg_stackoverflow__questions.sql
|   |   |-- stg_stackoverflow__answers.sql
|   |   |-- stg_stackoverflow__users.sql
|   |   `-- stg_stackoverflow__tags.sql
|   |-- intermediate/
|   |   |-- _intermediate_models.yml
|   |   |-- int_questions_with_answers.sql
|   |   |-- int_question_tag_exploded.sql
|   |   `-- int_user_question_activity.sql
|   `-- marts/
|       |-- _marts_models.yml
|       |-- mart_monthly_question_activity.sql
|       |-- mart_tag_activity.sql
|       |-- mart_answer_latency.sql
|       |-- mart_question_outcomes.sql
|       `-- mart_user_reputation_segments.sql
`-- tests/
    |-- assert_answer_latency_non_negative.sql
    |-- assert_mart_monthly_positive_counts.sql
    |-- assert_tag_activity_min_question_count.sql
    `-- assert_reputation_tier_coverage.sql
```

## Modeling Architecture

```text
bigquery-public-data.stackoverflow
          |
          v
staging views
  - one model per source table
  - year-window filter for large posts tables
  - column selection, casting, renaming
          |
          v
intermediate views
  - joins and enrichment
  - answer timing
  - tag explosion
  - user question activity
          |
          v
mart tables
  - final analytical outputs
  - persisted for cheaper review queries
```

Staging and intermediate models are views. Marts are BigQuery tables.

## Marts

| Mart | Grain | What it answers |
|---|---|---|
| `mart_monthly_question_activity` | Calendar month | Volume, resolution rates, and response-time trends |
| `mart_tag_activity` | Tag | Technology ecosystem health by tag |
| `mart_answer_latency` | Calendar month | First-answer and accepted-answer latency distributions |
| `mart_question_outcomes` | Question | Per-question outcome and score classification |
| `mart_user_reputation_segments` | Reputation tier | How user experience relates to question quality |

Full mart review guide: [docs/marts.md](docs/marts.md)

## Validation Surface

The validation surface is dbt plus BigQuery:

```bash
dbt debug
dbt deps
dbt run
dbt test
dbt docs generate
```

PowerShell wrappers are available from the repository root:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_debug.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_deps.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_docs_generate.ps1
.\projects\06-warehouse-first-analytics\scripts\dbt_workflow.ps1
```

More validation detail: [docs/validation.md](docs/validation.md)

## Local Validation Examples

Replace `your-project-id` with the GCP project configured in `profiles.yml`.

Monthly trend check:

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

Tag activity check:

```sql
select
  tag_name,
  questions_in_window,
  unanswered_rate_pct,
  accepted_answer_rate_pct
from `your-project-id.stackoverflow_analytics_marts.mart_tag_activity`
order by questions_in_window desc
limit 20;
```

Reputation segment check:

```sql
select
  reputation_tier,
  tier_rank,
  user_count,
  total_questions,
  avg_accepted_answer_rate_pct
from `your-project-id.stackoverflow_analytics_marts.mart_user_reputation_segments`
order by tier_rank;
```

## Windows-Native Setup

Install dependencies:

```powershell
cd projects\06-warehouse-first-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dbt\requirements.txt
python -m pip install -r requirements.txt
```

Authenticate:

```powershell
gcloud auth login
gcloud auth application-default login
gcloud config set project your-project-id
gcloud services enable bigquery.googleapis.com
```

Create the dbt profile:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.dbt"
Copy-Item "dbt\profiles.yml.example" "$HOME\.dbt\profiles.yml"
notepad "$HOME\.dbt\profiles.yml"
```

Set `project: your-gcp-project-id` in the profile.

## Cost Awareness

| Decision | Effect |
|---|---|
| Year-window filter in staging | Reduces large posts table scans |
| `stackoverflow_min_year` variable | Enables cheaper development windows |
| Exclude `body` columns | Avoids scanning large HTML text fields |
| Staging/intermediate as views | Avoids redundant persisted tables |
| Marts as tables | Makes review and downstream reads cheaper |
| `APPROX_QUANTILES` | Cheaper latency percentiles |
| Tag threshold | Keeps tag mart focused and smaller |

Estimated default full `dbt run`: about 15-20 GB scanned, roughly $0.09-$0.13 at on-demand pricing.

Cheaper development run:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -Select "+mart_monthly_question_activity" -MinYear 2023
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1 -Select mart_monthly_question_activity
```

Full cost discussion: [docs/cost-awareness.md](docs/cost-awareness.md)

## Tests

Schema tests live in model YAML files and validate model contracts:

```text
dbt/models/staging/_staging_models.yml
dbt/models/intermediate/_intermediate_models.yml
dbt/models/marts/_marts_models.yml
```

Singular tests live in `dbt/tests/` and validate business invariants:

- non-negative answer latency;
- positive monthly counts and valid rates;
- tag activity minimum question threshold;
- complete reputation-tier coverage.

Test rationale: [docs/tests.md](docs/tests.md)

## Known Limitations / Cost Notes

- The default year window is 2021-present. Earlier history is excluded by design for cost control.
- The public dataset refresh cadence is not controlled by this project.
- Source freshness tests are omitted because the public dataset refresh schedule is not reliable enough for v1.
- Raw question and answer HTML bodies are excluded; this is not a text analytics or NLP case.
- Accepted-answer joins can resolve to null when the accepted answer falls outside the selected year window.
- The project does not configure GCP budget alerts, scheduling, CI/CD, or production monitoring.
- Running `stackoverflow_min_year: 2008` is possible but intentionally more expensive.

## Screenshot Guidance

Useful portfolio screenshots:

- `dbt debug` with a successful BigQuery connection;
- `dbt run` showing mart models built;
- `dbt test` showing schema and singular tests passing;
- `dbt docs generate` completing successfully;
- BigQuery Explorer showing staging/intermediate views and mart tables;
- one or two mart query outputs from BigQuery.

Avoid presenting this project as a dashboard or API. The project artifact is the warehouse modeling
work: dbt SQL, tests, docs, lineage, BigQuery marts, and cost-aware decisions.

## Documentation

| Document | Contents |
|---|---|
| [docs/source.md](docs/source.md) | Source inspection, table schemas, caveats |
| [docs/modeling.md](docs/modeling.md) | Layer design and materialization decisions |
| [docs/marts.md](docs/marts.md) | Mart grain, caveats, and inspection queries |
| [docs/tests.md](docs/tests.md) | Schema and singular test rationale |
| [docs/cost-awareness.md](docs/cost-awareness.md) | Cost-control decisions |
| [docs/local-run.md](docs/local-run.md) | Setup, authentication, and run guide |
| [docs/validation.md](docs/validation.md) | dbt validation sequence and BigQuery checks |
| [notebooks/README.md](notebooks/README.md) | Optional source validation notebook guide |

## Future Directions

- Monthly incremental models for lower repeated build cost
- dbt exposures for downstream BI consumers
- Source freshness monitoring if refresh metadata becomes reliable
- Additional marts for tag trends and answer quality
- dbt artifact analysis for model runtime and build metadata
