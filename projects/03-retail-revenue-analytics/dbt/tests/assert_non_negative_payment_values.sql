select
    order_id,
    payment_sequential,
    payment_value
from {{ ref('stg_order_payments') }}
where payment_value < 0
