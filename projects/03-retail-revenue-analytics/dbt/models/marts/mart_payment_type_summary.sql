select
    payment_type,
    count(*) as payment_count,
    sum(payment_value) as total_payment_value,
    avg(payment_value) as average_payment_value
from {{ ref('stg_order_payments') }}
group by payment_type
