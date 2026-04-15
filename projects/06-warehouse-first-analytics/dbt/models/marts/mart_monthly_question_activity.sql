-- mart_monthly_question_activity
-- Grain: one row per calendar month within the staging window.
--
-- Summarizes the volume, engagement, and resolution rates of Stack Overflow
-- questions by month. Materialized as a table in BigQuery so downstream
-- consumers (notebooks, BI tools, ad-hoc queries) do not re-scan staging views.

with base as (

    select
        created_month_start,
        created_year,
        created_month,
        question_id,
        question_score,
        view_count,
        answer_count_in_window,
        has_accepted_answer,
        is_unanswered,
        hours_to_first_answer,
        hours_to_accepted_answer
    from {{ ref('int_questions_with_answers') }}

)

select
    created_month_start                                                     as month_start,
    created_year                                                            as year,
    created_month                                                           as month,

    -- Volume
    count(distinct question_id)                                             as total_questions,
    sum(case when is_unanswered then 1 else 0 end)                          as unanswered_questions,
    sum(case when has_accepted_answer then 1 else 0 end)                    as questions_with_accepted_answer,

    -- Resolution rates
    round(
        100.0 * sum(case when is_unanswered then 1 else 0 end)
        / nullif(count(distinct question_id), 0),
        2
    )                                                                       as unanswered_rate_pct,
    round(
        100.0 * sum(case when has_accepted_answer then 1 else 0 end)
        / nullif(count(distinct question_id), 0),
        2
    )                                                                       as accepted_answer_rate_pct,

    -- Engagement averages
    round(avg(question_score), 2)                                           as avg_question_score,
    round(avg(view_count), 0)                                               as avg_view_count,
    round(avg(answer_count_in_window), 2)                                   as avg_answer_count,

    -- Response time percentiles (hours)
    round(avg(hours_to_first_answer), 2)                                    as avg_hours_to_first_answer,
    round(
        approx_quantiles(hours_to_first_answer, 100)[offset(50)], 2
    )                                                                       as median_hours_to_first_answer,
    round(avg(hours_to_accepted_answer), 2)                                 as avg_hours_to_accepted_answer

from base
group by
    created_month_start,
    created_year,
    created_month
order by
    created_month_start
