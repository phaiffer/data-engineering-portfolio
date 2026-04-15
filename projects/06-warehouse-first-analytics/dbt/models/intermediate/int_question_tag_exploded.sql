-- int_question_tag_exploded
-- Grain: one row per (question, tag) pair.
--
-- Explodes the pipe-delimited tags_clean column from staging into individual
-- tag rows. This enables tag-level aggregations in mart_tag_activity without
-- requiring repeated string parsing in marts.
--
-- Implementation note:
--   BigQuery SPLIT() returns an ARRAY; UNNEST() flattens it to rows.
--   Tags with empty strings (edge case from malformed source rows) are excluded.

with questions as (

    select
        question_id,
        question_score,
        view_count,
        answer_count,
        has_accepted_answer,
        is_unanswered,
        created_year,
        created_month,
        created_month_start,
        tags_clean
    from {{ ref('stg_stackoverflow__questions') }}
    where tags_clean is not null
      and tags_clean != ''

)

select
    q.question_id,
    trim(tag)                   as tag_name,
    q.question_score,
    q.view_count,
    q.answer_count,
    q.has_accepted_answer,
    q.is_unanswered,
    q.created_year,
    q.created_month,
    q.created_month_start
from questions q,
unnest(split(q.tags_clean, '|')) as tag
where trim(tag) != ''
