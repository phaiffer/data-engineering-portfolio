# Tests

This project uses two categories of dbt tests: schema tests (YAML-defined, generic)
and singular tests (custom SQL assertions in `dbt/tests/`).

---

## Schema Tests

Schema tests are declared in `_staging_models.yml`, `_intermediate_models.yml`,
and `_marts_models.yml` alongside model documentation.

### Staging

| Model | Column | Test | Rationale |
|---|---|---|---|
| `stg_stackoverflow__questions` | `question_id` | not_null, unique | Each question must have a distinct ID |
| `stg_stackoverflow__questions` | `question_title` | not_null | Every question has a title |
| `stg_stackoverflow__questions` | `score` | not_null | Score defaults to 0, never truly null in source |
| `stg_stackoverflow__questions` | `view_count` | not_null | Same |
| `stg_stackoverflow__questions` | `answer_count` | not_null | Same |
| `stg_stackoverflow__questions` | `has_accepted_answer` | not_null, accepted_values(true/false) | Boolean derived column |
| `stg_stackoverflow__questions` | `is_unanswered` | not_null | Derived boolean |
| `stg_stackoverflow__questions` | `created_at` | not_null | Creation timestamp required |
| `stg_stackoverflow__questions` | `created_year` | not_null | Derived from creation_date |
| `stg_stackoverflow__questions` | `created_month` | not_null | Derived from creation_date |
| `stg_stackoverflow__questions` | `created_month_start` | not_null | Derived date truncation |
| `stg_stackoverflow__answers` | `answer_id` | not_null, unique | Each answer has a distinct ID |
| `stg_stackoverflow__answers` | `question_id` | not_null | Every answer must reference a question |
| `stg_stackoverflow__answers` | `score` | not_null | Same as questions |
| `stg_stackoverflow__answers` | `created_at` | not_null | Creation timestamp required |
| `stg_stackoverflow__users` | `user_id` | not_null, unique | Each real user has a distinct positive ID |
| `stg_stackoverflow__users` | `display_name` | not_null | Display name is required |
| `stg_stackoverflow__users` | `reputation` | not_null | Reputation defaults to 1 in source |
| `stg_stackoverflow__users` | `reputation_tier` | not_null, accepted_values | 5 defined tiers |
| `stg_stackoverflow__tags` | `tag_id` | not_null, unique | Each tag has a distinct ID |
| `stg_stackoverflow__tags` | `tag_name` | not_null, unique | Tag slug uniqueness |
| `stg_stackoverflow__tags` | `question_count` | not_null | Count is always present |

### Intermediate

| Model | Column | Test | Rationale |
|---|---|---|---|
| `int_questions_with_answers` | `question_id` | not_null, unique | Grain check |
| `int_questions_with_answers` | `question_created_at` | not_null | Required for latency calcs |
| `int_questions_with_answers` | `has_accepted_answer` | not_null | Required for outcome calcs |
| `int_questions_with_answers` | `created_month_start` | not_null | Required for time-series marts |
| `int_question_tag_exploded` | `question_id` | not_null | Each row must have a question |
| `int_question_tag_exploded` | `tag_name` | not_null | Each row must have a tag |
| `int_user_question_activity` | `user_id` | not_null, unique | Grain check |
| `int_user_question_activity` | `total_questions` | not_null | Aggregated count |

### Marts

| Model | Column | Test | Rationale |
|---|---|---|---|
| `mart_monthly_question_activity` | `month_start` | not_null, unique | One row per month |
| `mart_monthly_question_activity` | `total_questions` | not_null | Volume check |
| `mart_tag_activity` | `tag_name` | not_null, unique | One row per tag |
| `mart_tag_activity` | `questions_in_window` | not_null | Volume check |
| `mart_answer_latency` | `month_start` | not_null, unique | One row per month |
| `mart_answer_latency` | `questions_with_answers` | not_null | Denominator check |
| `mart_question_outcomes` | `question_id` | not_null, unique | One row per question |
| `mart_question_outcomes` | `outcome_category` | not_null, accepted_values | 4 valid outcomes |
| `mart_question_outcomes` | `score_tier` | not_null, accepted_values | 6 valid tiers |
| `mart_question_outcomes` | `created_month_start` | not_null | Date dimension |
| `mart_user_reputation_segments` | `reputation_tier` | not_null, unique, accepted_values | 5 tiers |
| `mart_user_reputation_segments` | `tier_rank` | not_null | Display ordering |
| `mart_user_reputation_segments` | `user_count` | not_null | Denominator check |
| `mart_user_reputation_segments` | `total_questions` | not_null | Volume check |

---

## Singular Tests

Custom SQL tests in `dbt/tests/`. Each test returns rows that fail the assertion;
a passing test returns zero rows.

### `assert_answer_latency_non_negative.sql`

Verifies that no question has a negative `hours_to_first_answer` or
`hours_to_accepted_answer`. A negative latency would indicate an answer
timestamped before its parent question, which is a source data quality issue.
This can occur in public datasets due to clock skew or ETL artifacts.

### `assert_mart_monthly_positive_counts.sql`

Verifies that every month in `mart_monthly_question_activity` has:
- At least 1 question
- `unanswered_rate_pct` between 0 and 100
- `accepted_answer_rate_pct` between 0 and 100
- The sum of both rates does not exceed 100 (they are not mutually inclusive by definition)

### `assert_tag_activity_min_question_count.sql`

Verifies that `mart_tag_activity` does not contain tags with fewer than 10 questions
in the window. The mart's `HAVING` clause enforces this, but the test catches any
future SQL drift that relaxes that threshold.

### `assert_reputation_tier_coverage.sql`

Verifies that all five expected reputation tiers appear in
`mart_user_reputation_segments`. A missing tier would indicate that no users from
that tier asked questions in the staging window, which would be unexpected for any
multi-year window and likely signals a modeling bug.

Stability note: this test is reliable for any window of 6+ months. For very narrow
windows (single month) the `expert` tier could theoretically be absent; in practice
this does not occur over multi-year defaults. The original draft used `at` as a CTE
alias, which is a reserved keyword in BigQuery SQL — corrected to unambiguous table
references.

---

## What is Not Tested

- **Relationship between answers and questions at staging level:** A cross-source
  relationship test (`stg_stackoverflow__answers.question_id` → `stg_stackoverflow__questions.question_id`)
  is intentionally omitted. Because both tables use the same year-window filter,
  answers to questions created before `stackoverflow_min_year` will have no matching
  question row. The relationship is valid in the source; the filter breaks it in the window.

- **Score range bounds:** No upper bound is tested on scores or view counts. The
  source dataset has legitimate extreme values (some questions have millions of views),
  and bounding them would produce noisy failures.

- **Freshness tests:** dbt source freshness checks require knowing the last refresh
  timestamp of the public dataset, which is not reliably documented. Omitted in v1.
