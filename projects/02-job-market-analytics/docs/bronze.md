# Bronze Layer

The Bronze layer is the first implemented step for the job market analytics case study.

## Scope

Bronze is responsible for:

- downloading the Kaggle dataset with `kagglehub`;
- landing raw files under `data/bronze/raw/ai_powered_job_market_insights/`;
- inventorying all landed files;
- selecting the main CSV for initial profiling;
- profiling the raw CSV with Pandas;
- writing a JSON metadata artifact under `data/bronze/metadata/`.

Bronze does not clean, rename, cast, deduplicate, or filter records.

## Dataset

- Kaggle handle: `uom190346a/ai-powered-job-market-insights`
- Local raw folder name: `ai_powered_job_market_insights`

## Main File Selection

If the dataset lands multiple CSV files, the Bronze profiler selects the largest supported CSV by file size, using the file path as a deterministic tie breaker.

This is intentionally simple for the raw foundation stage. Any stronger business-grain decision belongs in Silver or in documented source analysis after the file contents are reviewed.

## Metadata Captured

The Bronze metadata includes:

- dataset handle;
- local raw directory;
- generation timestamp in UTC;
- raw file inventory;
- selected main file;
- selection rule;
- row count;
- column count;
- raw column names;
- Pandas-inferred dtypes;
- null counts by column;
- duplicate row count;
- source notes and current scope notes.

## Run Commands

From the repository root:

```powershell
python projects/02-job-market-analytics/src/jobs/run_ingestion.py
python projects/02-job-market-analytics/src/jobs/run_bronze.py
```

## Current Notes

- The profiling engine is Pandas, matching the current local environment and avoiding unstable Spark usage.
- Bronze remains raw and intentionally does not apply business transformations.
- Downstream Silver, Gold, DBT DuckDB, DBT PostgreSQL, API, and dashboard layers are implemented outside the Bronze boundary.
