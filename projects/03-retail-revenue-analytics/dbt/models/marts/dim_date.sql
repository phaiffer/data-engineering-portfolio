select distinct
    order_purchase_date as date_day,
    extract(year from order_purchase_date) as year_number,
    extract(quarter from order_purchase_date) as quarter_number,
    extract(month from order_purchase_date) as month_number,
    strftime(order_purchase_date, '%B') as month_name,
    cast(strftime(order_purchase_date, '%V') as integer) as week_number,
    extract(day from order_purchase_date) as day_of_month,
    extract(dow from order_purchase_date) as day_of_week_number,
    strftime(order_purchase_date, '%A') as day_of_week_name
from {{ ref('int_order_items_enriched') }}
where order_purchase_date is not null
