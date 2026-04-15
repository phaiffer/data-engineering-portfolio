-- mart_question_outcomes
-- Grain: one row per question in the staging window.
--
-- Denormalized fact mart that carries one record per question with all relevant
-- outcome attributes. Useful for ad-hoc exploration, segmentation, and
-- downstream filtering without re-joining intermediate models.
--
-- This mart deliberately avoids body/text columns to minimize scan cost and
-- to remain focused on structured outcome metrics rather than NLP features.

select
    question_id,
    question_title,
    tags_clean,

    -- Scores and engagement
    question_score,
    view_count,
    answer_count,
    comment_count,
    favorite_count,

    -- Outcome flags
    has_accepted_answer,
    is_unanswered,

    -- Latency metrics (hours)
    hours_to_first_answer,
    hours_to_accepted_answer,

    -- Derived outcome category
    case
        when has_accepted_answer                            then 'resolved'
        when answer_count > 0 and not has_accepted_answer  then 'answered_no_accept'
        when is_unanswered                                 then 'unanswered'
        else                                                    'unknown'
    end                                                     as outcome_category,

    -- Score tier
    case
        when question_score >= 100  then 'viral'
        when question_score >= 25   then 'popular'
        when question_score >= 5    then 'good'
        when question_score >= 1    then 'decent'
        when question_score = 0     then 'neutral'
        else                             'downvoted'
    end                                                     as score_tier,

    -- Author context
    question_author_user_id,

    -- Date dimensions
    question_created_at,
    question_created_date,
    created_year,
    created_month,
    created_month_start

from {{ ref('int_questions_with_answers') }}
