# Silver Plan - Hospital Analytics

## Objective

Silver v1 standardizes the main Bronze patient flow CSV into a cleaner, typed, row-preserving dataset for later Gold modeling. It improves structure and technical consistency without creating business metrics or serving-ready aggregates.

The implementation uses Pandas while local PySpark remains blocked by local Java/Spark setup issues. The functions are kept small and layer-oriented so a future PySpark migration can keep the same orchestration shape.

## Working grain assumption

Current working assumption:

**1 row = 1 patient admission / patient flow event record**

This is a working assumption only. Silver preserves the raw row grain and does not deduplicate, filter, or aggregate records.

## Source

Bronze input dataset:

- `data/bronze/raw/healthcare_analytics_patient_flow/healthcare_analytics_patient_flow_data.csv`

Bronze profiling summary:

- Rows: 9216
- Columns: 11
- Duplicate rows: 0

## Raw-to-Silver rename mapping

Raw column | Silver column
--- | ---
`Patient Id` | `patient_id`
`Patient Admission Date` | `patient_admission_date`
`Patient Admission Time` | `patient_admission_time`
`Merged` | `merged_raw_value`
`Patient Gender` | `patient_gender`
`Patient Age` | `patient_age`
`Patient Race` | `patient_race`
`Department Referral` | `department_referral`
`Patient Admission Flag` | `patient_admission_flag`
`Patient Satisfaction Score` | `patient_satisfaction_score`
`Patient Waittime` | `patient_waittime`

## Type casting plan

Column | Silver handling
--- | ---
`patient_id` | Keep as nullable string after trimming
`patient_admission_date` | Parse to date where valid; invalid values become null-like date values
`patient_admission_time` | Normalize to `HH:MM:SS` where valid; invalid values become null
`patient_admission_timestamp` | Build from date and time where both parse safely
`patient_age` | Cast to Pandas nullable integer (`Int64`) where valid
`patient_satisfaction_score` | Cast to nullable numeric (`Float64`) while preserving nulls
`patient_waittime` | Cast to nullable numeric (`Float64`) while preserving nulls
String/category-like columns | Keep as nullable strings after trimming and blank-to-null cleanup
`silver_loaded_at_utc` | Add a UTC technical load timestamp

Safe parsing uses coercion instead of failing the whole job on isolated invalid values. Conversion summaries are emitted by lightweight quality checks so invalid parsing remains visible.

## Null handling

Silver v1 preserves source nulls and converts blank strings to nulls after trimming. It does not impute missing values, drop rows because of nulls, or replace high-null fields with defaults.

Known high-null fields remain nullable:

- `department_referral`
- `patient_satisfaction_score`

## In scope

- Resolve and load the main Bronze CSV
- Rename columns to stable snake_case names
- Trim string fields
- Convert blank strings to nulls
- Apply safe type normalization
- Build `patient_admission_timestamp` where parsing is valid
- Add `silver_loaded_at_utc`
- Preserve row count and row grain
- Write a local Silver CSV artifact
- Write lightweight Silver metadata JSON
- Run practical validation checks

## Out of scope

- PySpark, Spark, or Databricks execution
- Gold metrics or KPI generation
- Aggregation, deduplication, or row filtering
- PostgreSQL loading
- Serving views, Flask endpoints, or dashboard code
- Business interpretation of ambiguous fields
- Rewriting Bronze architecture

## Open semantic questions

- What does `Merged` represent? It is preserved as `merged_raw_value` until confirmed.
- What are the allowed values for `patient_admission_flag`?
- Is `patient_id` a true patient identifier or a synthetic event identifier?
- Should `patient_waittime` be interpreted in minutes?
- Is `patient_satisfaction_score` ordinal, categorical, or a numeric rating?

These questions should be resolved before designing Gold metrics.
