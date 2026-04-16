select
    order_id,
    order_item_id,
    product_id,
    customer_id,
    seller_id,
    store_id,
    salesperson_id,
    order_purchase_date
from {{ ref('fct_sales') }}
where product_id is null
   or customer_id is null
   or seller_id is null
   or store_id is null
   or salesperson_id is null
   or order_purchase_date is null
