# Job Market Analytics Documentation

This documentation folder tracks the implementation notes for `02-job-market-analytics`.

The current project stage is Bronze-first. It establishes raw source ingestion and profiling for the Kaggle dataset `uom190346a/ai-powered-job-market-insights`.

## Current Docs

- [Bronze](bronze.md): raw landing, file inventory, main CSV selection, and profiling metadata.
- [Silver Plan](silver_plan.md): Silver v1 grain, rename, type, null, and normalization plan.
- [Silver](silver.md): current row-preserving Silver implementation and run instructions.

## Roadmap Docs

Future documentation should be added only when those layers are implemented:

- Gold dimensional model and metric definitions.
- DBT model lineage and tests.
- Serving or dashboard notes if those layers are introduced later.
