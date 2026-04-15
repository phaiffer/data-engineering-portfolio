# Dimensional Modeling Plan

This document distinguishes the dimensional modeling direction, what is now implemented in DBT, and what remains unresolved.

## Implemented In This Phase

DBT DuckDB now implements a local dimensional modeling layer over the Python Silver outputs.

Implemented dimensions:

- `dim_product`
- `dim_customer`
- `dim_seller`
- `dim_date`

Implemented fact-like mart:

- `fct_sales`

Implemented business marts:

- `mart_daily_revenue`
- `mart_category_performance`
- `mart_seller_performance`
- `mart_customer_state_performance`
- `mart_order_status_summary`
- `mart_payment_type_summary`

The implemented model is intentionally modest. It proves dimensional modeling readiness and clear grain handling, but it is not a final enterprise warehouse design.

## Candidate Fact Grains

### Order Header Grain

One row per `order_id`.

Useful for order volume, order status, lifecycle timestamps, and customer order behavior.

Limitations:

- does not naturally represent product, seller, item price, or freight at line level;
- can hide multi-item orders.

### Order Item Grain

One row per `order_id` and `order_item_id`.

This is the implemented grain of `fct_sales`.

Useful for:

- item revenue;
- freight value;
- product category performance;
- seller performance;
- customer-state performance when joined through orders and customers.

This is the strongest primary analytical grain for retail revenue analytics because Olist item-side sales values live in `order_items.price` and `order_items.freight_value`.

### Payment Grain

One row per `order_id` and `payment_sequential`.

Useful for:

- payment method mix;
- installment behavior;
- total reported payment value;
- payment count per order.

Limitations:

- one order can have multiple payment rows;
- joining payments directly to order items can duplicate revenue;
- payment values should be reconciled separately from item-side sales measures.

## Payment Duplication Rule

Raw payment rows are not joined directly to item rows.

DBT implements `int_order_payments_summary` at one row per `order_id` before any payment context is available to `fct_sales`. This prevents raw payment rows from multiplying item-grain records.

Payment columns in `fct_sales` remain order-level context. They can repeat across item rows for multi-item orders and should not be summed as item-level revenue.

## Implemented Dimensions

- `dim_product`: product identity, category, physical attributes, translated category name.
- `dim_customer`: customer identity and coarse geography.
- `dim_seller`: seller identity and coarse geography.
- `dim_date`: purchase-date attributes based on dates present in item-grain sales.

Natural keys are retained. Surrogate keys are not introduced in this local portfolio phase because the source natural keys are clear enough for inspectable marts.

## Future Refinements

Potential future additions:

- `dim_order_status` if status semantics deserve their own descriptive table.
- `dim_geography` after geolocation deduplication rules are defined.
- `fact_orders` for order lifecycle analysis.
- `fact_payments` for payment behavior at payment sequence grain.
- reconciliation models comparing item-side totals to order-level payment totals.
- DBT exposures or docs generation if the project grows into a richer analytics-engineering case.

## Remaining Caveats

- The marts are not an accounting-grade revenue ledger.
- Refunds, cancellations, chargebacks, settlement timing, and tax/accounting recognition are not modeled.
- Order status is retained rather than silently filtering to delivered orders.
- PostgreSQL, orchestration, APIs, dashboards, and cloud deployment are outside this phase.
