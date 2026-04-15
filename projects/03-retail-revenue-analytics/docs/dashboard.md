# Dashboard Layer

The dashboard exists as the presentation layer for the retail revenue analytics case study. It turns the modeled marts and read-only API into a local, recruiter-friendly analytics experience without moving business logic into React.

## Role In The Architecture

The dashboard reads only from the local Flask API:

```text
React + Vite dashboard
-> Flask read-only API
-> DBT DuckDB marts
-> Silver source-aligned tables
```

It does not query DuckDB directly, run DBT, recalculate KPI definitions, or use mock analytics for the main experience.

## Local API Connectivity

The dashboard expects the API at:

```text
http://127.0.0.1:5002
```

The local Flask API is HTTP-only. A URL such as `https://127.0.0.1:5002` is wrong for this project and can produce browser SSL protocol errors.

Direct browser navigation to `/health` is not the same as a dashboard `fetch` request. Opening `/health` directly does not require CORS, while the dashboard does because it runs from a Vite origin such as `http://127.0.0.1:5173` or `http://127.0.0.1:5179`.

## Main Sections

- Overview header with scope notes and API connection status.
- KPI cards for orders, item rows, item revenue, freight, GMV, and item-side average order value.
- Daily revenue trend using item revenue and gross merchandise value.
- Top category performance by gross merchandise value.
- Top seller performance with seller state context.
- Customer state performance by customer geography.
- Order status summary with order counts and item-side GMV.
- Payment type summary with payment counts and payment values.

## KPI Definitions

The KPI cards come directly from `/api/v1/kpis`:

- `total_orders`: distinct orders in `fct_sales`.
- `total_order_items`: item-grain rows in `fct_sales`.
- `total_item_revenue`: sum of item price.
- `total_freight_value`: sum of item-side freight value.
- `total_gross_merchandise_value`: item revenue plus freight value.
- `average_order_value_item_side`: item-side revenue divided by distinct orders.

These values are analytical item-side measures. They are not accounting-grade revenue, settlement, refund, tax, or revenue-recognition metrics.

## Payment Caveat

Payment summaries describe payment behavior by payment type. They are useful for understanding payment mix, counts, total payment value, and average payment value. They should not be read as item-level sales revenue.

## Error And Empty States

The dashboard has section-level loading, empty, and error states. If the API is not running or an endpoint fails, the affected section displays the failure honestly. Other sections can still render if their API calls succeed.

The dashboard header shows the configured API base URL and the current frontend origin to make local CORS and protocol issues easier to diagnose.

## Troubleshooting

Wrong:

```text
https://127.0.0.1:5002
```

Right:

```text
http://127.0.0.1:5002
```

If the API is reachable directly but unavailable from the dashboard, check:

- `VITE_API_BASE_URL` in `dashboard/.env`;
- the dashboard origin and Vite port;
- `RETAIL_REVENUE_API_CORS_ALLOWED_ORIGINS`;
- `RETAIL_REVENUE_API_ALLOW_LOCAL_DEV_CORS`;
- browser console messages for CORS, SSL, or generic fetch failures.

## Non-Goals

- No authentication or authorization.
- No cloud infrastructure.
- No orchestration.
- No write behavior.
- No BI-tool clone or complex query builder.
- No production commerce application claims.
