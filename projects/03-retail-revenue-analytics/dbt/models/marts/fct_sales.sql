select
    items.order_id,
    items.order_item_id,
    items.product_id,
    items.customer_id,
    items.seller_id,
    items.order_purchase_timestamp,
    items.order_purchase_date,
    items.order_status,
    items.customer_state,
    items.seller_state,
    items.product_category_name,
    items.product_category_name_english,
    items.item_price,
    items.freight_value,
    items.gross_merchandise_value,
    payments.payment_value_total,
    payments.payment_record_count,
    payments.payment_installments_total,
    payments.payment_types_used
from {{ ref('int_order_items_enriched') }} as items
left join {{ ref('int_order_payments_summary') }} as payments
    on items.order_id = payments.order_id
