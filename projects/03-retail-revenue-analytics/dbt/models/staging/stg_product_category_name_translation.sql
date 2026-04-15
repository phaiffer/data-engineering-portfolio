select
    cast(product_category_name as varchar) as product_category_name,
    cast(product_category_name_english as varchar) as product_category_name_english
from {{ source('silver', 'product_category_name_translation') }}
