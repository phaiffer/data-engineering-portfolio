-- stg_stackoverflow__questions
-- Grain: one row per Stack Overflow question.
--
-- Cost-aware design:
--   The posts_questions table in bigquery-public-data is not partitioned.
--   The creation_date filter below restricts the scan to a configurable
--   year window, set by the `stackoverflow_min_year` dbt variable (default 2021).
--   Without this filter a full-table scan would process ~70 GB+.
--   This model materializes as a VIEW so the filter is always pushed to the
--   source; downstream models that ref() this view inherit the predicate.

with source as (

    select
        id,
        title,
        tags,
        score,
        view_count,
        answer_count,
        comment_count,
        favorite_count,
        accepted_answer_id,
        owner_user_id,
        creation_date,
        last_activity_date
    from {{ source('stackoverflow', 'posts_questions') }}
    where
        -- Cost control: limit scan to questions created from this year onward.
        -- The full table covers 2008-present; recent years are the most analytically
        -- relevant and substantially reduce query cost.
        extract(year from creation_date) >= {{ var('stackoverflow_min_year') }}

)

select
    id                                                  as question_id,
    title                                               as question_title,
    -- Normalize tag string: strip angle brackets and replace >< delimiter with |
    replace(replace(tags, '<', ''), '>', '|')           as tags_raw,
    -- Remove trailing pipe left by the replace above
    regexp_replace(
        replace(replace(tags, '<', ''), '>', '|'),
        r'\|$', ''
    )                                                   as tags_clean,
    cast(score as int64)                                as score,
    cast(view_count as int64)                           as view_count,
    cast(answer_count as int64)                         as answer_count,
    cast(comment_count as int64)                        as comment_count,
    coalesce(cast(favorite_count as int64), 0)          as favorite_count,
    accepted_answer_id,
    owner_user_id,
    -- Derived convenience columns
    (accepted_answer_id is not null)                    as has_accepted_answer,
    (answer_count = 0)                                  as is_unanswered,
    cast(creation_date as timestamp)                    as created_at,
    cast(last_activity_date as timestamp)               as last_active_at,
    date(creation_date)                                 as created_date,
    extract(year from creation_date)                    as created_year,
    extract(month from creation_date)                   as created_month,
    date_trunc(date(creation_date), month)              as created_month_start
from source
