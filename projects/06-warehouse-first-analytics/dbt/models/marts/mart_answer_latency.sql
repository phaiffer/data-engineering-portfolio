-- mart_answer_latency
-- Grain: one row per calendar month within the staging window.
--
-- Focuses on response time: how quickly does the community answer questions?
-- Provides median and percentile latency distributions useful for tracking
-- community health trends over time.
--
-- Separate from mart_monthly_question_activity to keep latency analytics
-- clean and independently queryable without joining to volume metrics.

with base as (

    select
        created_month_start,
        created_year,
        created_month,
        question_id,
        has_accepted_answer,
        hours_to_first_answer,
        hours_to_accepted_answer,
        answer_count_in_window
    from {{ ref('int_questions_with_answers') }}
    -- Only include questions where at least one answer exists in the window
    where answer_count_in_window > 0

)

select
    created_month_start                                                     as month_start,
    created_year                                                            as year,
    created_month                                                           as month,

    -- Sample size
    count(distinct question_id)                                             as questions_with_answers,
    count(distinct case when has_accepted_answer then question_id end)      as questions_with_accepted_answer,

    -- First-answer latency distribution (hours)
    round(avg(hours_to_first_answer), 2)                                    as avg_hours_to_first_answer,
    round(
        approx_quantiles(hours_to_first_answer, 100)[offset(25)], 2
    )                                                                       as p25_hours_to_first_answer,
    round(
        approx_quantiles(hours_to_first_answer, 100)[offset(50)], 2
    )                                                                       as median_hours_to_first_answer,
    round(
        approx_quantiles(hours_to_first_answer, 100)[offset(75)], 2
    )                                                                       as p75_hours_to_first_answer,
    round(
        approx_quantiles(hours_to_first_answer, 100)[offset(90)], 2
    )                                                                       as p90_hours_to_first_answer,

    -- Accepted-answer latency distribution (hours, only for questions with accepted answer)
    round(avg(
        case when has_accepted_answer then hours_to_accepted_answer end
    ), 2)                                                                   as avg_hours_to_accepted_answer,
    round(
        approx_quantiles(
            case when has_accepted_answer then hours_to_accepted_answer end,
            100
        )[offset(50)], 2
    )                                                                       as median_hours_to_accepted_answer

from base
group by
    created_month_start,
    created_year,
    created_month
order by
    created_month_start
