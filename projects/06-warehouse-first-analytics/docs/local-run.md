# Local Run Guide

This guide walks through the complete setup from a fresh machine to running dbt
against BigQuery.

---

## Prerequisites

- Python 3.10 or later
- A Google Cloud Platform account (free tier is sufficient for development)
- `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install

---

## Step 1: GCP Project Setup

If you do not have a GCP project, create one:

```bash
gcloud projects create your-project-id --name="stackoverflow-analytics"
gcloud config set project your-project-id
```

Enable the BigQuery API:

```bash
gcloud services enable bigquery.googleapis.com
```

---

## Step 2: Authentication

### Option A: OAuth (recommended for local development)

```bash
gcloud auth application-default login
```

This writes a credential file to `~/.config/gcloud/application_default_credentials.json`.
dbt will pick it up automatically when `method: oauth` is set in the profile.

### Option B: Service Account

Create a service account and download a JSON key:

```bash
gcloud iam service-accounts create dbt-sa \
    --display-name="dbt BigQuery service account"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:dbt-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding your-project-id \
    --member="serviceAccount:dbt-sa@your-project-id.iam.gserviceaccount.com" \
    --role="roles/bigquery.jobUser"

gcloud iam service-accounts keys create /path/to/sa-key.json \
    --iam-account=dbt-sa@your-project-id.iam.gserviceaccount.com
```

Then set in your profile: `method: service-account` and `keyfile: /path/to/sa-key.json`.

---

## Step 3: Python Environment

From the project root (`projects/06-warehouse-first-analytics/`):

```bash
python -m venv .venv
source .venv/bin/activate

# dbt BigQuery adapter
pip install -r dbt/requirements.txt

# Notebook and validation dependencies (optional)
pip install -r requirements.txt
```

---

## Step 4: dbt Profile

Copy the example profile and edit it:

```bash
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
```

Edit `~/.dbt/profiles.yml`:

```yaml
stackoverflow_analytics:
  target: bigquery
  outputs:
    bigquery:
      type: bigquery
      method: oauth
      project: your-gcp-project-id    # <-- replace
      dataset: stackoverflow_analytics
      location: US
      threads: 4
      timeout_seconds: 300
```

---

## Step 5: Validate Connection

```bash
cd dbt/
dbt debug
```

Expected output includes:
```
Connection test: [OK connection ok]
```

If this fails, check that:
1. `project` in profiles.yml matches your GCP project ID
2. BigQuery API is enabled in that project
3. Your credentials have `bigquery.dataEditor` and `bigquery.jobUser` roles

---

## Step 6: Install dbt Packages

```bash
dbt deps
```

This installs `dbt-labs/dbt_utils` from `packages.yml`.

---

## Step 7: Run dbt

### Full pipeline (recommended)

```bash
bash scripts/run_dbt_bigquery.sh
```

This runs: `dbt debug` → `dbt deps` → `dbt run` → `dbt test`

### Individual commands

```bash
# Build all models
dbt run

# Run only staging models
dbt run --select staging

# Run only marts
dbt run --select marts

# Run a specific model and its upstream dependencies
dbt run --select +mart_monthly_question_activity

# Run all tests
dbt test

# Run tests for a specific model
dbt test --select mart_question_outcomes

# Generate and serve documentation
dbt docs generate
dbt docs serve
```

---

## Step 8: Restrict the Year Window (Cost Control)

The default window is 2021–present. To reduce scan cost during development:

```bash
# 2023–present only (lowest cost)
dbt run --vars '{"stackoverflow_min_year": 2023}'

# 2022–present
dbt run --vars '{"stackoverflow_min_year": 2022}'
```

See [cost-awareness.md](cost-awareness.md) for the full cost discussion.

---

## Step 9: Validate Results

After a successful `dbt run`, query the marts directly in BigQuery:

```sql
-- Check monthly question volume
SELECT month_start, total_questions, accepted_answer_rate_pct
FROM `your-project-id.stackoverflow_analytics_marts.mart_monthly_question_activity`
ORDER BY month_start;

-- Top 10 tags by question volume
SELECT tag_name, questions_in_window, accepted_answer_rate_pct
FROM `your-project-id.stackoverflow_analytics_marts.mart_tag_activity`
ORDER BY questions_in_window DESC
LIMIT 10;
```

Or use the source validation notebook:

```bash
cd notebooks/
jupyter notebook 01_source_validation.ipynb
```

---

## Validation Status

**dbt debug** and the BigQuery connection were confirmed to work correctly with the
`phaiffertech` GCP project during development (dbt-core 1.11.8, dbt-bigquery 1.11.1,
oauth authentication). `dbt run` and `dbt test` require Application Default Credentials
(`gcloud auth application-default login`) which must be set up interactively per the
instructions above.

The `dbt debug` command confirms:
- `profiles.yml` is valid
- `dbt_project.yml` is valid
- `bigquery` adapter version is detected correctly
- Connection succeeds once ADC credentials are in place

`dbt run` and `dbt test` have not been executed end-to-end in CI for this portfolio
project; they require a GCP project with BigQuery enabled and appropriate IAM permissions.
The SQL models have been reviewed for correctness against the BigQuery dialect, and all
known syntax issues (reserved keyword aliases, function compatibility) have been addressed.

---

## Troubleshooting

**`404 Not found: Dataset` error**
dbt creates the target dataset automatically. If it fails, create it manually:
```bash
bq mk --dataset your-project-id:stackoverflow_analytics
```

**`Access Denied: BigQuery BigQuery: Permission denied`**
Ensure your account/service account has both `bigquery.dataEditor` and
`bigquery.jobUser` IAM roles on your project.

**`Quota exceeded` or `bytes billed` errors**
Reduce the year window: `dbt run --vars '{"stackoverflow_min_year": 2023}'`

**`dbt debug` reports `profiles.yml not found`**
Ensure you copied `profiles.yml.example` to `~/.dbt/profiles.yml` (not to the dbt/ directory).
The `profiles.yml` in the dbt/ directory is gitignored to avoid committing credentials.
