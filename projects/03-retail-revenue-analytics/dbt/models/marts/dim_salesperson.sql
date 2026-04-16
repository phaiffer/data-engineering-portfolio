select
    seller_id as salesperson_id,
    seller_id as store_id,
    seller_city as salesperson_city,
    seller_state as salesperson_state
from {{ ref('stg_sellers') }}
