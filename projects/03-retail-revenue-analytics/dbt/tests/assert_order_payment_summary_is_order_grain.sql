select
    order_id,
    count(*) as row_count
from {{ ref('int_order_payments_summary') }}
group by order_id
having count(*) > 1
