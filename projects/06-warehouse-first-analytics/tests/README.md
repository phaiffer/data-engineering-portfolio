# tests/

This directory is reserved for project-level integration tests and validation
scripts that operate outside of dbt.

In v1, all testing lives inside the dbt project:

- **Schema tests** (not_null, unique, accepted_values, relationships) are declared
  in YAML files alongside each model layer:
  - `dbt/models/staging/_staging_models.yml`
  - `dbt/models/intermediate/_intermediate_models.yml`
  - `dbt/models/marts/_marts_models.yml`

- **Singular tests** (custom SQL assertions) live in:
  - `dbt/tests/assert_answer_latency_non_negative.sql`
  - `dbt/tests/assert_mart_monthly_positive_counts.sql`
  - `dbt/tests/assert_tag_activity_min_question_count.sql`
  - `dbt/tests/assert_reputation_tier_coverage.sql`

Run all tests with:

```bash
cd dbt/
dbt test
```

See [../docs/tests.md](../docs/tests.md) for a full test inventory and rationale.

## Future additions

If this project grows to include Python validation scripts or end-to-end
acceptance tests outside of dbt, they would live here.
