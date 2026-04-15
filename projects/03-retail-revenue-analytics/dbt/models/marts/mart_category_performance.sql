select
    product_category_name,
    product_category_name_english,
    count(*) as order_item_count,
    sum(item_price) as item_revenue,
    sum(freight_value) as freight_value,
    sum(gross_merchandise_value) as gross_merchandise_value
from {{ ref('fct_sales') }}
group by
    product_category_name,
    product_category_name_english
