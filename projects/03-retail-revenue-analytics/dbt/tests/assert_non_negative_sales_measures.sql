select
    order_id,
    order_item_id,
    item_price,
    freight_value,
    gross_merchandise_value
from {{ ref('fct_sales') }}
where item_price < 0
   or freight_value < 0
   or gross_merchandise_value < 0
