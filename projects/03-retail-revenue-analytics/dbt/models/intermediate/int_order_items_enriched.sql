with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

category_translation as (
    select * from {{ ref('stg_product_category_name_translation') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

sellers as (
    select * from {{ ref('stg_sellers') }}
)

select
    order_items.order_id,
    order_items.order_item_id,
    order_items.product_id,
    order_items.seller_id,
    orders.customer_id,
    orders.order_status,
    orders.order_purchase_timestamp,
    cast(orders.order_purchase_timestamp as date) as order_purchase_date,
    extract(year from orders.order_purchase_timestamp) as order_purchase_year,
    extract(month from orders.order_purchase_timestamp) as order_purchase_month,
    extract(day from orders.order_purchase_timestamp) as order_purchase_day,
    order_items.shipping_limit_date,
    customers.customer_unique_id,
    customers.customer_zip_code_prefix,
    customers.customer_city,
    customers.customer_state,
    sellers.seller_zip_code_prefix,
    sellers.seller_city,
    sellers.seller_state,
    products.product_category_name,
    coalesce(
        category_translation.product_category_name_english,
        products.product_category_name,
        'unknown'
    ) as product_category_name_english,
    products.product_name_length,
    products.product_description_length,
    products.product_photos_qty,
    products.product_weight_g,
    products.product_length_cm,
    products.product_height_cm,
    products.product_width_cm,
    order_items.item_price,
    order_items.freight_value,
    order_items.item_price + order_items.freight_value as gross_merchandise_value
from order_items
left join orders
    on order_items.order_id = orders.order_id
left join products
    on order_items.product_id = products.product_id
left join category_translation
    on products.product_category_name = category_translation.product_category_name
left join customers
    on orders.customer_id = customers.customer_id
left join sellers
    on order_items.seller_id = sellers.seller_id
