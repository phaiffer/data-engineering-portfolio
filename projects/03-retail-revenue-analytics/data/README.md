# Local Data Area

This directory is reserved for local medallion-aligned artifacts for the retail revenue analytics project.

Expected local layout:

```text
data/
  bronze/
    raw/
    metadata/
  silver/
    tables/
    metadata/
  gold/
    outputs/
    metadata/
```

Bronze raw files are landed locally from Kaggle and kept unchanged. Silver tables are source-aligned standardized CSVs. Gold outputs are first-pass analytical summaries for revenue and business KPI inspection.

Raw files and generated artifacts are local outputs. Recreate them by running the ingestion, Bronze, Silver, and Gold jobs from the repository root.
