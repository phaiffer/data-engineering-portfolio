# Gold Layer

Gold v1 creates local analytical CSV outputs for first-pass retail revenue and business KPI review.

Gold v1 is useful for portfolio inspection, but it is not a finished accounting model and not a final dimensional mart design.

## Run Command

From the repository root:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_gold.py
```

Run Silver first if the Silver tables are not present:

```powershell
python projects/03-retail-revenue-analytics/src/jobs/run_silver.py
```

## Outputs

Gold CSV artifacts are written to:

```text
data/gold/outputs/
```

Implemented outputs:

- `kpi_overview.csv`
- `daily_revenue_summary.csv`
- `category_revenue_summary.csv`
- `seller_revenue_summary.csv`
- `customer_state_revenue_summary.csv`
- `payment_type_summary.csv`
- `order_status_summary.csv`

Run-level metadata is written to:

```text
data/gold/metadata/gold_run_summary.json
```

## Revenue Definitions

Gold v1 uses item-side sales measures from `order_items`:

- `item_revenue = sum(order_items.price)`
- `freight_value = sum(order_items.freight_value)`
- `gross_merchandise_value = sum(order_items.price + order_items.freight_value)`

Payments are summarized separately by payment type. They are not joined to item rows for revenue totals because one order can have multiple payment rows.

## Output Notes

### kpi_overview.csv

Compact metric table with metric name, value, scope, and notes. It includes distinct order counts, order item counts, item revenue, freight value, gross merchandise value, average order item value, and reported payment value.

### daily_revenue_summary.csv

Daily item-side revenue by purchase date and order status. Status remains visible so users can decide whether to analyze all orders or only delivered orders later.

### category_revenue_summary.csv

Item-side revenue by raw product category and English category translation. If translation is missing, the raw category name is retained instead of dropping the row.

### seller_revenue_summary.csv

Item-side revenue by seller and seller state.

### customer_state_revenue_summary.csv

Item-side revenue by customer state, with distinct order counts and item counts.

### payment_type_summary.csv

Payment behavior summary by payment type. This output uses `order_payments` only and does not define sales revenue.

### order_status_summary.csv

Item-side revenue grouped by order status.

## Limitations

- No refund, cancellation, chargeback, or settlement reconciliation is implemented.
- No accounting revenue recognition rules are applied.
- No final fact or dimension tables are created.
- No DBT marts are implemented yet.
- Order status is retained rather than silently filtering to delivered orders.
- Payment values are kept separate from item-side revenue to avoid accidental double counting.
