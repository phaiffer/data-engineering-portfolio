select
    order_id,
    count(*) as payment_record_count,
    sum(payment_value) as payment_value_total,
    sum(payment_installments) as payment_installments_total,
    avg(payment_value) as average_payment_value,
    min(payment_value) as min_payment_value,
    max(payment_value) as max_payment_value,
    string_agg(distinct payment_type, ', ' order by payment_type) as payment_types_used
from {{ ref('stg_order_payments') }}
group by order_id
