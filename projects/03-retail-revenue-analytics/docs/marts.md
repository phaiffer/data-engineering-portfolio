# Dimensional Marts

The DBT mart layer turns the source-aligned Silver outputs into dimensional analytical contracts.

These marts are local, inspectable, and portfolio-oriented. They are not an enterprise dimensional model and not an accounting-grade revenue ledger.

## Dimensions

### dim_product

Grain: one row per `product_id`.

Includes raw and English category labels plus product attributes such as name length, description length, photo quantity, weight, and dimensions.

### dim_customer

Grain: one row per `customer_id`.

Includes customer unique identity and coarse customer geography.

### dim_seller

Grain: one row per `seller_id`.

Includes seller zip prefix, city, and state.

### dim_date

Grain: one row per purchase date represented in item-grain sales data.

Includes year, quarter, month, week, day of month, and day of week attributes.

## Fact-Like Mart

### fct_sales

Grain: one row per `order_id` and `order_item_id`.

This is the central analytical sales fact-like mart. It joins order item rows to order, product, category, customer, seller, date, and order-grain payment context.

Measures:

- `item_price`: item price from `order_items`.
- `freight_value`: item-level freight value.
- `gross_merchandise_value`: `item_price + freight_value`.

Payment fields are joined only after `order_payments` is aggregated to one row per order. This avoids multiplying item rows by raw payment rows.

Payment fields in `fct_sales` are order-level context. They can repeat across multi-item orders and should not be summed as item-level sales revenue.

## Business Marts

### mart_daily_revenue

Grain: one row per purchase date and order status.

Metrics include distinct order count, order item count, item revenue, freight value, and gross merchandise value.

### mart_category_performance

Grain: one row per product category.

Uses translated category labels where available and keeps safe fallbacks for missing translations.

### mart_seller_performance

Grain: one row per seller.

Useful for seller-level item-side revenue and freight review.

### mart_customer_state_performance

Grain: one row per customer state.

Useful for regional customer demand analysis.

### mart_order_status_summary

Grain: one row per order status.

Keeps status visible so delivered, canceled, shipped, and other statuses are not silently mixed.

### mart_payment_type_summary

Grain: one row per payment type.

This is payment behavior analysis, not item-side sales revenue.

## Caveats

- No final accounting revenue recognition is implemented.
- Refunds, cancellations, chargebacks, and settlement timing are not reconciled.
- The dimensional model is intentionally modest and local-first.
- PostgreSQL, orchestration, serving APIs, dashboards, and cloud deployment are not included in this phase.
