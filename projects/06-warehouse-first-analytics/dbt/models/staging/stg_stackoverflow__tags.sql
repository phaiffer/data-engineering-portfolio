-- stg_stackoverflow__tags
-- Grain: one row per distinct tag. Very small table (~65 k rows).
-- No cost filter required; this is a reference/dimension table.

with source as (

    select
        id,
        tag_name,
        count,
        excerpt_post_id,
        wiki_post_id
    from {{ source('stackoverflow', 'tags') }}
    where tag_name is not null

)

select
    id                          as tag_id,
    lower(trim(tag_name))       as tag_name,
    cast(count as int64)        as question_count,
    excerpt_post_id,
    wiki_post_id
from source
