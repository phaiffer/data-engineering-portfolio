select
    seller_id as store_id,
    seller_id,
    seller_zip_code_prefix as store_zip_code_prefix,
    seller_city as store_city,
    seller_state as store_state
from {{ ref('stg_sellers') }}
