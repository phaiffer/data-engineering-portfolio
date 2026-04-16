# KPI Definitions

These metrics are designed for item-grain retail revenue analysis over the modeled `fct_sales` mart.

`fct_sales` grain: one row per sold item per order, identified by `order_id` and `order_item_id`.

| KPI | Formula | Business meaning |
| --- | --- | --- |
| `gross_revenue` | `sum(item_price + freight_value)` | Total item-side commercial value including freight. Useful for high-level demand and logistics-inclusive revenue views. |
| `net_revenue` | `sum(item_price)` | Item revenue before freight, refunds, taxes, chargebacks, and settlement timing. This is the primary product-sales measure in this project. |
| `units_sold` | `count(*)` from `fct_sales` | Number of sold item rows at the declared fact grain. |
| `order_count` | `count(distinct order_id)` | Number of unique customer orders represented in the mart. |
| `average_order_value` | `sum(item_price) / count(distinct order_id)` | Average item revenue per order. Freight is excluded to keep product demand separate from delivery cost. |
| `discount_amount` | Not available in the Olist source tables used here. | Placeholder KPI for future datasets with list price or promotion fields. It is documented but not calculated to avoid inventing data. |
| `discount_rate` | Not available without `discount_amount` or list price. | Future promotion effectiveness metric once discount inputs exist. |
| `margin` / `profit` | Not available without product cost, fees, taxes, or settlement data. | Future profitability KPI. Current outputs should be read as revenue analytics, not profit analytics. |

## Payment Caveat

Payment rows can be one-to-many with orders. They are aggregated to order grain before being attached to `fct_sales`, and payment totals are treated as order-level context. They should not be summed across item rows because that would overstate revenue for multi-item orders.
