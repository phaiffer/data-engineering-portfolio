-- int_user_question_activity
-- Grain: one row per user in the staging window who has asked at least one question.
--
-- Summarizes each user's question-asking behavior over the scoped time window.
-- Joined with user reputation context from staging for downstream mart use.

with questions as (

    select
        question_id,
        question_author_user_id,
        question_score,
        view_count,
        has_accepted_answer,
        is_unanswered,
        question_created_at,
        created_year
    from {{ ref('int_questions_with_answers') }}
    where question_author_user_id is not null

),

users as (

    select
        user_id,
        display_name,
        reputation,
        reputation_tier,
        account_created_date
    from {{ ref('stg_stackoverflow__users') }}

),

question_agg as (

    select
        question_author_user_id                                         as user_id,
        count(*)                                                        as total_questions,
        sum(case when has_accepted_answer then 1 else 0 end)            as questions_with_accepted_answer,
        sum(case when is_unanswered then 1 else 0 end)                  as unanswered_questions,
        round(avg(question_score), 2)                                   as avg_question_score,
        round(avg(view_count), 0)                                       as avg_question_views,
        max(question_created_at)                                        as most_recent_question_at,
        min(question_created_at)                                        as first_question_in_window_at
    from questions
    group by question_author_user_id

)

select
    qa.user_id,
    u.display_name,
    u.reputation,
    u.reputation_tier,
    u.account_created_date,
    qa.total_questions,
    qa.questions_with_accepted_answer,
    qa.unanswered_questions,
    qa.avg_question_score,
    qa.avg_question_views,
    qa.most_recent_question_at,
    qa.first_question_in_window_at,
    -- Acceptance rate (null-safe)
    case
        when qa.total_questions > 0
        then round(
            100.0 * qa.questions_with_accepted_answer / qa.total_questions, 1
        )
        else null
    end                                                                 as accepted_answer_rate_pct
from question_agg qa
left join users u
    on qa.user_id = u.user_id
