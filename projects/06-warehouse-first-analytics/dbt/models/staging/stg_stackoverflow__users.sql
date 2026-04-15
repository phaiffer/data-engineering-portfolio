-- stg_stackoverflow__users
-- Grain: one row per registered Stack Overflow user (id > 0).
--
-- The users table is small relative to posts (~5 M rows) so no year filter
-- is applied here. System and anonymous user stubs (id <= 0) are excluded.

with source as (

    select
        id,
        display_name,
        reputation,
        up_votes,
        down_votes,
        views,
        location,
        creation_date,
        last_access_date
    from {{ source('stackoverflow', 'users') }}
    where id > 0

)

select
    id                                          as user_id,
    display_name,
    cast(reputation as int64)                   as reputation,
    cast(up_votes as int64)                     as up_votes,
    cast(down_votes as int64)                   as down_votes,
    cast(views as int64)                        as profile_views,
    nullif(trim(location), '')                  as location,
    cast(creation_date as timestamp)            as account_created_at,
    cast(last_access_date as timestamp)         as last_access_at,
    date(creation_date)                         as account_created_date,
    extract(year from creation_date)            as account_created_year,
    -- Simple reputation tier segmentation
    case
        when reputation >= 100000 then 'expert'
        when reputation >= 10000  then 'advanced'
        when reputation >= 1000   then 'established'
        when reputation >= 100    then 'contributor'
        else                           'new'
    end                                         as reputation_tier
from source
