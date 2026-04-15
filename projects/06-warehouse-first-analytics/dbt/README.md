# dbt — Stack Overflow Analytics

This directory contains the dbt project for the warehouse-first analytics case.

## Structure

```
dbt/
├── dbt_project.yml          # project name, profile, materialization config
├── profiles.yml.example     # copy to ~/.dbt/profiles.yml and fill in GCP details
├── packages.yml             # dbt_utils dependency
├── requirements.txt         # pip install -r requirements.txt
├── scripts/
│   └── run_dbt_bigquery.sh  # end-to-end: debug → deps → run → test
├── macros/                  # shared macros (none required for v1)
├── models/
│   ├── staging/             # one view per source table
│   ├── intermediate/        # enrichment and join models
│   └── marts/               # final tables materialized in BigQuery
└── tests/                   # singular (custom SQL) tests
```

## Quick start

```bash
# 1. Install dbt
pip install -r requirements.txt

# 2. Configure BigQuery profile
cp profiles.yml.example ~/.dbt/profiles.yml
# Edit ~/.dbt/profiles.yml with your GCP project ID

# 3. Authenticate (oauth path)
gcloud auth application-default login

# 4. Run everything
bash scripts/run_dbt_bigquery.sh
```

See [../docs/local-run.md](../docs/local-run.md) for full setup instructions.

## Cost awareness

Staging models include a `creation_date >= YYYY-01-01` filter controlled by the
`stackoverflow_min_year` variable (default: 2021). This limits BigQuery scan volume
to roughly 4 years of data instead of the full historical table (~70 GB+).

Override at runtime:

```bash
dbt run --vars '{"stackoverflow_min_year": 2022}'
```
