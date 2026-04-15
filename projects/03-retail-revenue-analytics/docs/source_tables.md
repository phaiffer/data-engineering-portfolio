# Olist Source Tables

This page documents the raw source files landed from Kaggle dataset `olistbr/brazilian-ecommerce`.

Bronze inventories every landed file. Silver v1 intentionally processes only the core sales and entity tables needed for source-aligned retail analytics. Geolocation and reviews are documented but deferred from Silver v1.

## Landed Files

```text
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
product_category_name_translation.csv
```

## Core Tables

### orders

- Source file: `olist_orders_dataset.csv`
- Business role: order header and order lifecycle table.
- Likely raw grain: one row per `order_id`.
- Important columns: `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`, `order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`, `order_estimated_delivery_date`.
- Likely joins: joins to `customers` on `customer_id`; joins to `order_items`, `order_payments`, and `order_reviews` on `order_id`.
- Retail analytics value: provides order status and lifecycle dates for volume, delivery, and status-aware revenue summaries.
- Silver v1 scope: included.

### order_items

- Source file: `olist_order_items_dataset.csv`
- Business role: purchased item lines within orders.
- Likely raw grain: one row per `order_id` and `order_item_id`.
- Important columns: `order_id`, `order_item_id`, `product_id`, `seller_id`, `shipping_limit_date`, `price`, `freight_value`.
- Likely joins: joins to `orders` on `order_id`, `products` on `product_id`, and `sellers` on `seller_id`.
- Retail analytics value: strongest first candidate for item-side sales metrics such as item revenue, freight value, category performance, and seller performance.
- Silver v1 scope: included.

### order_payments

- Source file: `olist_order_payments_dataset.csv`
- Business role: payment records for orders.
- Likely raw grain: one row per order payment sequence, represented by `order_id` and `payment_sequential`.
- Important columns: `order_id`, `payment_sequential`, `payment_type`, `payment_installments`, `payment_value`.
- Likely joins: joins to `orders` on `order_id`.
- Retail analytics value: useful for payment behavior, installment analysis, and payment-method mix.
- Silver v1 scope: included.
- Modeling caution: payments should not be naively joined to order items for revenue totals because one order can have multiple payment rows.

### products

- Source file: `olist_products_dataset.csv`
- Business role: product attributes.
- Likely raw grain: one row per `product_id`.
- Important columns: `product_id`, `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`, `product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`.
- Likely joins: joins to `order_items` on `product_id`; joins to `product_category_name_translation` on `product_category_name`.
- Retail analytics value: enables category performance and future product dimension modeling.
- Silver v1 scope: included.
- Source note: the raw file uses `lenght` in two column names; Silver v1 preserves that source spelling.

### product_category_name_translation

- Source file: `product_category_name_translation.csv`
- Business role: Portuguese-to-English product category lookup.
- Likely raw grain: one row per `product_category_name`.
- Important columns: `product_category_name`, `product_category_name_english`.
- Likely joins: joins to `products` on `product_category_name`.
- Retail analytics value: makes category summaries easier to read while retaining the raw category name.
- Silver v1 scope: included.

### customers

- Source file: `olist_customers_dataset.csv`
- Business role: customer order identity and coarse geography.
- Likely raw grain: one row per `customer_id`.
- Important columns: `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`, `customer_city`, `customer_state`.
- Likely joins: joins to `orders` on `customer_id`.
- Retail analytics value: enables customer-state performance and future customer/geography dimensions.
- Silver v1 scope: included.

### sellers

- Source file: `olist_sellers_dataset.csv`
- Business role: seller identity and coarse geography.
- Likely raw grain: one row per `seller_id`.
- Important columns: `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`.
- Likely joins: joins to `order_items` on `seller_id`.
- Retail analytics value: enables seller performance and future seller dimension modeling.
- Silver v1 scope: included.

## Deferred Tables

### order_reviews

- Source file: `olist_order_reviews_dataset.csv`
- Business role: customer review feedback after orders.
- Likely raw grain: one row per review event, usually connected to an `order_id`.
- Important columns: `review_id`, `order_id`, `review_score`, `review_comment_title`, `review_comment_message`, `review_creation_date`, `review_answer_timestamp`.
- Likely joins: joins to `orders` on `order_id`.
- Retail analytics value: useful for satisfaction and quality analysis.
- Silver v1 scope: deferred to keep the first Silver and Gold layers focused on revenue and order behavior.

### geolocation

- Source file: `olist_geolocation_dataset.csv`
- Business role: zip-code-prefix geolocation reference.
- Likely raw grain: multiple rows per `geolocation_zip_code_prefix` can exist because the file contains repeated latitude/longitude observations.
- Important columns: `geolocation_zip_code_prefix`, `geolocation_lat`, `geolocation_lng`, `geolocation_city`, `geolocation_state`.
- Likely joins: can support customer and seller geography through zip code prefixes, but requires deduplication or geospatial modeling decisions first.
- Retail analytics value: useful for future geography enrichment.
- Silver v1 scope: deferred because it is large and needs explicit geography rules before becoming a stable Silver contract.
