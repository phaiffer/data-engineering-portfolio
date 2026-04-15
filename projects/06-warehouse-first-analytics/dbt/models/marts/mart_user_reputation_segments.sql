-- mart_user_reputation_segments
-- Grain: one row per reputation tier.
--
-- Aggregates question-asking behavior by reputation segment to show
-- how user experience level correlates with question quality and outcomes.
-- Derived from int_user_question_activity which already scopes to the
-- staging window.

with user_activity as (

    select
        user_id,
        reputation,
        reputation_tier,
        total_questions,
        questions_with_accepted_answer,
        unanswered_questions,
        avg_question_score,
        avg_question_views,
        accepted_answer_rate_pct
    from {{ ref('int_user_question_activity') }}
    where reputation_tier is not null

)

select
    reputation_tier,

    -- Tier ordering for display purposes
    case reputation_tier
        when 'new'         then 1
        when 'contributor' then 2
        when 'established' then 3
        when 'advanced'    then 4
        when 'expert'      then 5
    end                                                     as tier_rank,

    -- User counts
    count(distinct user_id)                                 as user_count,

    -- Question volume
    sum(total_questions)                                    as total_questions,
    sum(questions_with_accepted_answer)                     as questions_with_accepted_answer,
    sum(unanswered_questions)                               as unanswered_questions,

    -- Averages
    round(avg(total_questions), 2)                          as avg_questions_per_user,
    round(avg(avg_question_score), 2)                       as avg_question_score,
    round(avg(avg_question_views), 0)                       as avg_question_views,
    round(avg(accepted_answer_rate_pct), 2)                 as avg_accepted_answer_rate_pct,

    -- Reputation stats within tier
    min(reputation)                                         as min_reputation_in_tier,
    max(reputation)                                         as max_reputation_in_tier,
    round(avg(reputation), 0)                               as avg_reputation_in_tier

from user_activity
group by reputation_tier
order by tier_rank
