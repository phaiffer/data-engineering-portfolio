# Data Quality And Rerun Safety

The project keeps validation close to the current local implementation style: Python jobs emit run metadata, and dbt tests validate the modeled analytical contract.

## Data Quality Checks

Implemented dbt checks cover:

- no nulls in critical keys for staging, dimensions, and `fct_sales`;
- uniqueness for dimensions and declared natural grains;
- referential integrity from `fct_sales` to `dim_date`, `dim_product`, `dim_customer`, `dim_seller`, `dim_store`, and `dim_salesperson`;
- no duplicate `fct_sales` rows at the declared `order_id` and `order_item_id` grain;
- non-negative sales and payment measures;
- valid purchase dates aligned between timestamp and date fields;
- order-grain payment summaries before payment context is joined to item-grain facts.

Run the dbt validation suite from `projects/03-retail-revenue-analytics/dbt`:

```bash
python -m dbt.cli.main test --profiles-dir . --target duckdb
```

## Rerun Safety

The local jobs are batch-oriented and overwrite generated outputs rather than appending to them:

- Silver rewrites source-aligned CSV tables under `data/silver/tables`.
- Gold rewrites KPI summary CSV outputs under `data/gold/outputs`.
- dbt rebuilds DuckDB mart tables from Silver inputs.

This makes reruns idempotent for the same raw inputs. Duplicate protection is handled through source-grain tests and mart-grain tests rather than hidden mutation logic.

## Incremental Assumptions

The current dataset is a static analytical export, so full-batch rebuilds are simpler and safer than incremental loads. If the source became operational, the natural next step would be date-partitioned processing by `order_purchase_date`, with a small lookback window for late-arriving order items, payments, or status changes.

Late-arriving or duplicate records would be handled by:

- reprocessing the affected purchase-date partition;
- deduplicating on the natural grain for each source table;
- aggregating payments to order grain before joining to item-grain facts;
- running dbt tests before publishing dashboard-facing marts.

## Observability

Silver and Gold jobs write structured run metrics into their run metadata JSON artifacts and print the same metrics in the local CLI output. Metrics include:

- execution start and end timestamps;
- job status;
- rows read;
- rows written;
- invalid row count;
- rejected row count.
