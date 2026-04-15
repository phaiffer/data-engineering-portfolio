select
    order_purchase_date,
    order_status,
    count(distinct order_id) as order_count,
    count(*) as order_item_count,
    sum(item_price) as item_revenue,
    sum(freight_value) as freight_value,
    sum(gross_merchandise_value) as gross_merchandise_value
from {{ ref('fct_sales') }}
group by
    order_purchase_date,
    order_status
