# Silver Layer

The Silver layer standardizes selected Olist source tables into local, source-aligned CSV artifacts.

## Run Command

From the repository root:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
```

Run ingestion first if the raw files are not landed:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_ingestion.py
```

## Outputs

Silver table artifacts are written to:

```text
data/silver/tables/
```

Metadata artifacts are written to:

```text
data/silver/metadata/
```

Implemented Silver v1 tables:

```text
orders.csv
order_items.csv
order_payments.csv
products.csv
product_category_name_translation.csv
customers.csv
sellers.csv
```

## Metadata

Each table metadata file includes:

- dataset handle;
- logical table name;
- raw source file path;
- output file path;
- generation timestamp in UTC;
- row count;
- column count;
- column names;
- Pandas dtypes;
- null counts;
- duplicate row count;
- grain preservation and scope notes.

The run summary is written to:

```text
data/silver/metadata/silver_run_summary.json
```

## Scope Notes

Silver v1 is not a dimensional layer. It is a stable local foundation for future modeling.

Allowed standardization is intentionally conservative:

- column-name normalization;
- whitespace trimming;
- blank string to null conversion;
- configured datetime parsing;
- configured numeric parsing.

Silver v1 does not join all sources together, deduplicate records, aggregate metrics, define revenue, or create surrogate keys.
