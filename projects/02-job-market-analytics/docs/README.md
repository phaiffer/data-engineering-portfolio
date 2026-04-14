# Job Market Analytics Docs

Curated documentation index for `02-job-market-analytics`.

Use this folder to review how the case moves from raw Kaggle data into modeled analytical outputs, then into the API and dashboard read layer.

## Start Here

- [Project README](../README.md): portfolio case-study overview, architecture flow, local run path, and current status.
- [Assets](assets/README.md): dashboard screenshot inventory and future presentation assets.

## Pipeline Layers

- [Bronze](bronze.md): raw landing, file inventory, source selection, and profiling metadata.
- [Silver](silver.md): row-preserving standardization of job-market records.
- [Gold](gold.md): Python-generated analytical summaries for the local medallion path.

## Modeling

- [DBT project](../dbt/README.md): DuckDB and PostgreSQL DBT execution notes.
- [Silver Plan](silver_plan.md): design notes for the first Silver implementation.
- [Gold Plan](gold_plan.md): design notes for the first Gold implementation.

## Read Layer

- [API docs](api.md): read-only Flask endpoints over PostgreSQL Silver data and DBT marts.
- [API README](../api/README.md): concise run instructions and endpoint list for the API package.

## Portfolio Review Path

For a quick reviewer walkthrough:

1. Read the [Project README](../README.md) for the case positioning.
2. Open [Bronze](bronze.md), [Silver](silver.md), and [Gold](gold.md) to understand the Python medallion flow.
3. Review the [DBT project](../dbt/README.md) to see the dual DuckDB and PostgreSQL modeling paths.
4. Check [API docs](api.md) for the dashboard read layer.
5. Use [Assets](assets/README.md) to locate the current dashboard screenshot.
