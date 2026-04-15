# Dimensional Modeling Plan

This document outlines the likely modeling direction for future iterations. The dimensional model is not implemented yet.

## Candidate Fact Grains

### Order Header Grain

One row per `order_id`.

Useful for:

- order volume;
- order status;
- lifecycle timestamps;
- customer order behavior.

Limitations:

- does not naturally represent product, seller, item price, or freight at line level;
- can hide multi-item orders.

### Order Item Grain

One row per `order_id` and `order_item_id`.

Useful for:

- item revenue;
- freight value;
- product category performance;
- seller performance;
- customer-state performance when joined through orders and customers.

This is likely the best primary analytical grain for retail revenue analytics because Olist item-side sales values live in `order_items.price` and `order_items.freight_value`.

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

## Why Payments Are Kept Separate

Payments are not used as the base revenue grain in Gold v1. A naive join between `order_payments` and `order_items` can multiply values when an order has multiple payment rows or multiple item rows.

Future modeling can reconcile order-level payment totals to item-side sales totals, but that should be an explicit model with documented allocation or reconciliation rules.

## Likely Future Dimensions

- `dim_product`: product identity, category, physical attributes, translated category name.
- `dim_customer`: customer identity and coarse geography.
- `dim_seller`: seller identity and coarse geography.
- `dim_date`: reusable date attributes for purchase, approval, delivery, and shipping dates.
- `dim_order_status`: optional status dimension if status semantics become richer.
- `dim_geography`: possible later dimension after geolocation deduplication rules are defined.

## Likely Future Facts

- `fact_order_items`: likely primary revenue fact at order item grain.
- `fact_orders`: order lifecycle and status fact at order grain.
- `fact_payments`: payment behavior fact at payment sequence grain.

## Likely Future KPIs

- order volume;
- orders with item rows;
- average order value;
- item revenue;
- freight value;
- gross merchandise value;
- category performance;
- seller performance;
- customer-state performance;
- payment-type mix;
- order-status distribution.

## Current Boundary

The current implementation stops at source-aligned Silver tables and Gold v1 summary CSVs. It does not create final dimensional marts, DBT models, orchestration, serving APIs, dashboards, or accounting-grade revenue reconciliation.
