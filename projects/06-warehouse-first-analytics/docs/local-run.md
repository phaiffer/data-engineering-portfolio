# Local Run Guide

This guide walks through the complete setup from a fresh machine to running dbt against BigQuery.
The workflow is intentionally warehouse-first: there is no local ingestion layer, no local database,
no API, and no dashboard.

## Prerequisites

- Python 3.10 or later
- A Google Cloud Platform project
- BigQuery API enabled
- Google Cloud CLI installed: `https://cloud.google.com/sdk/docs/install`
- A billing account or free-tier setup appropriate for BigQuery public dataset queries

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

PowerShell uses the same commands:

```powershell
gcloud projects create your-project-id --name="stackoverflow-analytics"
gcloud config set project your-project-id
gcloud services enable bigquery.googleapis.com
```

## Step 2: Authentication

### Option A: OAuth For Local Development

```bash
gcloud auth login
gcloud auth application-default login
```

On Windows, this opens a browser and writes Application Default Credentials under:

```text
%APPDATA%\gcloud\application_default_credentials.json
```

dbt will use this automatically when `method: oauth` is set in the profile.

### Option B: Service Account

Create a service account and download a JSON key:

```bash
gcloud iam service-accounts create dbt-sa --display-name="dbt BigQuery service account"
gcloud projects add-iam-policy-binding your-project-id --member="serviceAccount:dbt-sa@your-project-id.iam.gserviceaccount.com" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding your-project-id --member="serviceAccount:dbt-sa@your-project-id.iam.gserviceaccount.com" --role="roles/bigquery.jobUser"
gcloud iam service-accounts keys create C:\path\to\sa-key.json --iam-account=dbt-sa@your-project-id.iam.gserviceaccount.com
```

Then set in your profile: `method: service-account` and `keyfile: C:\path\to\sa-key.json`.
Do not commit credential files.

## Step 3: Python Environment

From the project root (`projects/06-warehouse-first-analytics/`):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r dbt/requirements.txt
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
cd projects\06-warehouse-first-analytics
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dbt\requirements.txt
python -m pip install -r requirements.txt
```

## Step 4: dbt Profile

Create the dbt profile directory if needed, then copy the example profile:

```bash
mkdir -p ~/.dbt
cp dbt/profiles.yml.example ~/.dbt/profiles.yml
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force -Path "$HOME\.dbt"
Copy-Item "dbt\profiles.yml.example" "$HOME\.dbt\profiles.yml"
notepad "$HOME\.dbt\profiles.yml"
```

Edit `profiles.yml`:

```yaml
stackoverflow_analytics:
  target: bigquery
  outputs:
    bigquery:
      type: bigquery
      method: oauth
      project: your-gcp-project-id
      dataset: stackoverflow_analytics
      location: US
      threads: 4
      timeout_seconds: 300
```

The configured dataset is the base schema. dbt appends layer schemas, producing datasets such as:

```text
stackoverflow_analytics_staging
stackoverflow_analytics_intermediate
stackoverflow_analytics_marts
```

## Step 5: Validate Connection

From `projects/06-warehouse-first-analytics/dbt/`:

```bash
dbt debug
```

From the repository root on PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_debug.ps1
```

Expected output includes:

```text
Connection test: [OK connection ok]
```

If this fails, check that the profile project ID is correct, BigQuery API is enabled, and your
credentials have `bigquery.dataEditor` and `bigquery.jobUser` roles.

## Step 6: Install dbt Packages

```bash
dbt deps
```

PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_deps.ps1
```

This installs `dbt-labs/dbt_utils` from `packages.yml`.

## Step 7: Run dbt

Full workflow from PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_workflow.ps1
```

Cheaper development workflow:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_workflow.ps1 -MinYear 2023
```

Equivalent individual commands:

```bash
dbt debug
dbt deps
dbt run
dbt test
dbt docs generate
```

Useful model selection examples:

```bash
dbt run --select staging
dbt run --select marts
dbt run --select +mart_monthly_question_activity
dbt test --select mart_question_outcomes
```

PowerShell wrappers:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -Select staging
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -Select "+mart_monthly_question_activity"
.\projects\06-warehouse-first-analytics\scripts\dbt_test.ps1 -Select mart_question_outcomes
.\projects\06-warehouse-first-analytics\scripts\dbt_docs_generate.ps1
```

## Step 8: Restrict the Year Window

The default window is 2021-present. To reduce scan cost during development:

```bash
dbt run --vars '{"stackoverflow_min_year": 2023}'
```

PowerShell:

```powershell
.\projects\06-warehouse-first-analytics\scripts\dbt_run.ps1 -MinYear 2023
```

Use narrow year windows while developing SQL. Use the default project setting for the full
portfolio build.

## Step 9: Validate Results

After a successful `dbt run`, query the marts directly in BigQuery:

```sql
select month_start, total_questions, accepted_answer_rate_pct
from `your-project-id.stackoverflow_analytics_marts.mart_monthly_question_activity`
order by month_start desc
limit 12;
```

```sql
select tag_name, questions_in_window, accepted_answer_rate_pct
from `your-project-id.stackoverflow_analytics_marts.mart_tag_activity`
order by questions_in_window desc
limit 10;
```

More validation queries are in [validation.md](validation.md).

## Validation Status

`dbt debug` and the BigQuery connection were confirmed to work with the `phaiffertech` GCP project
during development using oauth authentication. `dbt run`, `dbt test`, and `dbt docs generate`
require Application Default Credentials set up interactively on the reviewer machine.

This project does not run end-to-end in local CI because it depends on a GCP project, BigQuery API,
IAM permissions, and the BigQuery public dataset. The SQL models and tests are written for the
BigQuery dialect and are intended to be validated through dbt against BigQuery.

## Troubleshooting

**`404 Not found: Dataset` error**

dbt usually creates target datasets automatically. If it fails, create the base dataset manually:

```bash
bq mk --dataset your-project-id:stackoverflow_analytics
```

**`Access Denied: BigQuery BigQuery: Permission denied`**

Ensure your account or service account has both `bigquery.dataEditor` and `bigquery.jobUser` IAM
roles on your project.

**`Quota exceeded` or `bytes billed` errors**

Reduce the year window:

```bash
dbt run --vars '{"stackoverflow_min_year": 2023}'
```

**`dbt debug` reports `profiles.yml not found`**

Ensure you copied `profiles.yml.example` to `$HOME\.dbt\profiles.yml` on Windows or
`~/.dbt/profiles.yml` on macOS/Linux. The real `profiles.yml` is gitignored.
