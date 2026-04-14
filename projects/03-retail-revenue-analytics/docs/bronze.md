# Bronze Layer

The Bronze layer is the first implemented step for the retail revenue analytics case study.

## Responsibilities

Bronze is responsible for:

- downloading the Kaggle dataset with `kagglehub`;
- landing raw files under `data/bronze/raw/olist_brazilian_ecommerce/`;
- inventorying all landed files, including hidden Kaggle operational artifacts;
- identifying supported CSV files that are eligible for lightweight profiling;
- selecting one main CSV for initial profiling;
- profiling that raw CSV with Pandas;
- writing a readable JSON metadata artifact under `data/bronze/metadata/`.

Bronze does not clean, rename, cast business types, deduplicate, filter, aggregate, create business keys, or define fact/dimension semantics.

## Dataset

- Kaggle handle: `olistbr/brazilian-ecommerce`
- Local raw folder name: `olist_brazilian_ecommerce`
- Supported raw file extensions for Bronze profiling: `.csv`

## Main File Selection Rule

If the dataset lands multiple CSV files, the Bronze profiler selects the largest supported CSV by file size, using the file path as a deterministic tie breaker.

This is only a raw-stage profiling rule. It is not the final analytical fact-grain decision, and it does not mean the selected CSV is the future sales fact table. Olist contains multiple related tables, so the final business grain must be decided later from the relationships between orders, order items, payments, customers, sellers, products, and dates.

## Metadata Captured

The Bronze metadata includes:

- dataset handle;
- local raw directory;
- generation timestamp in UTC;
- complete raw file inventory;
- selected main file;
- main file selection rule;
- profiling summary;
- source notes;
- Bronze scope notes.

The profiling summary includes:

- profiled file;
- profiling engine;
- row count;
- column count;
- raw column names;
- Pandas-inferred dtypes;
- null counts by column;
- duplicate row count.

## Run Commands

From the repository root:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
python projects/03-retail-revenue-analytics/src/jobs/run_bronze.py
```

## Current Notes

- Pandas is used for local profiling.
- Spark is intentionally not introduced in this phase.
- Hidden Kaggle operational artifacts are inventoried but excluded from Bronze profiling.
- Bronze remains raw so future Silver and dimensional modeling decisions stay inspectable.
- Fact, dimension, Gold KPI, DBT, orchestration, API, dashboard, and cloud layers are deferred.
