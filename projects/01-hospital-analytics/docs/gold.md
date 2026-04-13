# Gold Layer - Hospital Analytics

Gold v1 creates small, curated analytical outputs from the Silver patient flow dataset. These outputs are designed for future PostgreSQL loading, API exposure, and dashboard usage while keeping the current implementation local and Pandas-based.

The Gold layer uses only the Silver artifact as its source:

```text
data/silver/healthcare_analytics_patient_flow_silver.csv
```

It does not go back to Bronze, reinterpret raw fields, or add unsupported medical/business semantics.

## Outputs

### `daily_patient_flow.csv`

Grain: 1 row per `admission_date`.

Columns:

- `admission_date`
- `total_patient_events`
- `average_patient_waittime`
- `average_patient_satisfaction_score`
- `admitted_patient_events`
- `null_department_referral_events`
- `null_satisfaction_score_events`

`admitted_patient_events` counts records where `patient_admission_flag` equals the exact Silver value `Admission`. This is a simple categorical count, not a broader clinical interpretation.

### `department_referral_summary.csv`

Grain: 1 row per `department_referral` value.

Columns:

- `department_referral`
- `total_patient_events`
- `average_patient_waittime`
- `average_patient_satisfaction_score`
- `share_of_total_events`

Missing department referrals are preserved with `groupby(dropna=False)` and written as blank/null values in the CSV output. This avoids silently dropping a large portion of the source events.

### `demographic_summary.csv`

Grain: 1 row per `patient_gender`, `patient_race`, and `patient_age_band`.

Columns:

- `patient_gender`
- `patient_race`
- `patient_age_band`
- `total_patient_events`
- `average_patient_waittime`
- `average_patient_satisfaction_score`

Age bands are intentionally simple:

- `0_17`
- `18_35`
- `36_50`
- `51_65`
- `66_plus`

## Null Handling

Pandas averages ignore null numeric values by default. Gold keeps this behavior for wait time and satisfaction score averages.

For count metrics, Gold uses explicit event counts and explicit null counts where useful. Null department referrals remain visible in the department referral summary instead of being filtered out.

## Why These Outputs Matter

These files establish the first consumption-ready analytical layer:

- Daily patient flow can support operational trend reporting.
- Department referral summary can support service-line volume and referral mix reporting.
- Demographic summary can support high-level segmentation for dashboard exploration.

The files are intentionally simple CSV artifacts for now, which makes them easy to inspect locally and straightforward to load into PostgreSQL or expose through APIs later.

## How to Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/src/jobs/run_gold.py
```

If your virtual environment is already activated:

```powershell
python projects/01-hospital-analytics/src/jobs/run_gold.py
```

Expected outputs:

```text
projects/01-hospital-analytics/data/gold/daily_patient_flow.csv
projects/01-hospital-analytics/data/gold/department_referral_summary.csv
projects/01-hospital-analytics/data/gold/demographic_summary.csv
projects/01-hospital-analytics/data/gold/gold_metadata.json
```

## Out of Scope

Gold v1 does not:

- Use PySpark or Databricks-specific logic.
- Load data into PostgreSQL.
- Create serving views.
- Build Flask API endpoints.
- Build dashboard code.
- Create DBT marts.
- Infer semantics for `merged_raw_value`.
- Rewrite Bronze or Silver architecture.
