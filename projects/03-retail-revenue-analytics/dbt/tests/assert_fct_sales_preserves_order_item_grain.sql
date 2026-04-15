with order_item_count as (
    select count(*) as row_count
    from {{ ref('stg_order_items') }}
),

fact_count as (
    select count(*) as row_count
    from {{ ref('fct_sales') }}
)

select
    fact_count.row_count as fact_row_count,
    order_item_count.row_count as order_item_row_count
from fact_count
cross join order_item_count
where fact_count.row_count != order_item_count.row_count
