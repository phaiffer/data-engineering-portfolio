select
    order_id,
    order_item_id,
    order_purchase_timestamp,
    order_purchase_date
from {{ ref('fct_sales') }}
where order_purchase_date is null
   or order_purchase_date < date '2016-01-01'
   or order_purchase_date > current_date
   or cast(order_purchase_timestamp as date) != order_purchase_date
