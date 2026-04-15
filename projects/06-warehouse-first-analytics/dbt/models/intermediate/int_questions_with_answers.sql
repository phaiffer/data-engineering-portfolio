-- int_questions_with_answers
-- Grain: one row per question in the staging window.
--
-- Joins question-level attributes with aggregated answer metrics,
-- and attaches the earliest accepted answer's creation timestamp where
-- an accepted_answer_id exists.
--
-- This model provides the enriched question row used by:
--   - mart_monthly_question_activity
--   - mart_answer_latency
--   - mart_question_outcomes

with questions as (

    select * from {{ ref('stg_stackoverflow__questions') }}

),

answers as (

    select * from {{ ref('stg_stackoverflow__answers') }}

),

-- Aggregate answers per question: first answer time, best score, count
answer_agg as (

    select
        question_id,
        count(*)                        as posted_answer_count,
        max(score)                      as top_answer_score,
        min(created_at)                 as first_answer_at
    from answers
    group by question_id

),

-- Identify the accepted answer's creation timestamp
accepted_answers as (

    select
        a.question_id,
        a.answer_id                     as accepted_answer_id,
        a.created_at                    as accepted_answer_created_at,
        a.owner_user_id                 as accepted_answer_author_user_id
    from answers a
    inner join questions q
        on a.answer_id = q.accepted_answer_id

)

select
    q.question_id,
    q.question_title,
    q.tags_clean,
    q.score                                                             as question_score,
    q.view_count,
    q.answer_count,
    q.comment_count,
    q.favorite_count,
    q.has_accepted_answer,
    q.is_unanswered,
    q.owner_user_id                                                     as question_author_user_id,
    q.created_at                                                        as question_created_at,
    q.created_date                                                      as question_created_date,
    q.created_year,
    q.created_month,
    q.created_month_start,

    -- Answer aggregates (null if no answers exist in the staging window)
    coalesce(aa.posted_answer_count, 0)                                 as answer_count_in_window,
    aa.top_answer_score,
    aa.first_answer_at,

    -- Time-to-first-answer in hours (null if no answers)
    case
        when aa.first_answer_at is not null
        then timestamp_diff(aa.first_answer_at, q.created_at, minute) / 60.0
        else null
    end                                                                 as hours_to_first_answer,

    -- Accepted answer details (null if no accepted answer)
    acc.accepted_answer_id,
    acc.accepted_answer_created_at,
    acc.accepted_answer_author_user_id,

    -- Time-to-accepted-answer in hours (null if no accepted answer)
    case
        when acc.accepted_answer_created_at is not null
        then timestamp_diff(acc.accepted_answer_created_at, q.created_at, minute) / 60.0
        else null
    end                                                                 as hours_to_accepted_answer

from questions q
left join answer_agg aa
    on q.question_id = aa.question_id
left join accepted_answers acc
    on q.question_id = acc.question_id
