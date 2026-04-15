# Silver Plan

Silver v1 is source-aligned. It standardizes selected raw Olist tables enough to make them easier to inspect and reuse, but it does not turn them into final facts or dimensions.

## Strategy

Silver v1 preserves the row grain of each selected source table:

- `orders`: order header grain.
- `order_items`: order item grain.
- `order_payments`: payment sequence grain.
- `products`: product grain.
- `product_category_name_translation`: category lookup grain.
- `customers`: customer order identity grain.
- `sellers`: seller grain.

The output contract is one Silver CSV per selected raw source table.

## What Silver Does

- Resolves the source registry from landed raw files.
- Reads selected raw CSV files.
- Normalizes column names to lowercase snake case when needed.
- Trims text whitespace.
- Converts blank strings to nulls.
- Parses configured datetime columns.
- Parses configured numeric columns.
- Writes one CSV per source-aligned table under `data/silver/tables/`.
- Writes one JSON metadata file per table under `data/silver/metadata/`.
- Writes one Silver run summary JSON.

## What Silver Does Not Do

- No business aggregation.
- No row deletion because a record looks unusual.
- No deduplication.
- No surrogate keys.
- No dimensional modeling as final tables.
- No giant denormalized Silver table.
- No hidden revenue logic.
- No joins as canonical Silver outputs.

## Silver v1 In Scope

```text
orders
order_items
order_payments
products
product_category_name_translation
customers
sellers
```

These tables are enough to support a cautious first Gold layer for order, item-side revenue, category, seller, customer-state, payment-type, and order-status summaries.

## Deferred From Silver v1

```text
order_reviews
geolocation
```

Reviews are valuable for customer satisfaction analysis, but they are not needed for the first revenue-focused outputs. Geolocation is valuable but requires explicit rules for repeated zip-code-prefix records before it should become a stable Silver contract.

## Design Rationale

Olist is a multi-table marketplace dataset. Source-aligned Silver tables keep the raw relationships visible and avoid prematurely hiding grain decisions inside a denormalized dataset.

This makes later dimensional modeling easier to review because future facts and dimensions can be traced back to stable source-aligned Silver tables.
