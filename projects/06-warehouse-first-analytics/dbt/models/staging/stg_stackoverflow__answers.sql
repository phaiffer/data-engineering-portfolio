-- stg_stackoverflow__answers
-- Grain: one row per Stack Overflow answer.
--
-- Cost-aware design:
--   Same year-window filter as stg_stackoverflow__questions.
--   Both tables are unpartitioned in the public dataset; all cost control
--   is achieved through creation_date predicates.

with source as (

    select
        id,
        parent_id,
        score,
        comment_count,
        owner_user_id,
        creation_date,
        last_activity_date
    from {{ source('stackoverflow', 'posts_answers') }}
    where
        extract(year from creation_date) >= {{ var('stackoverflow_min_year') }}

)

select
    id                                      as answer_id,
    parent_id                               as question_id,
    cast(score as int64)                    as score,
    cast(comment_count as int64)            as comment_count,
    owner_user_id,
    cast(creation_date as timestamp)        as created_at,
    cast(last_activity_date as timestamp)   as last_active_at,
    date(creation_date)                     as created_date,
    extract(year from creation_date)        as created_year,
    extract(month from creation_date)       as created_month,
    date_trunc(date(creation_date), month)  as created_month_start
from source
