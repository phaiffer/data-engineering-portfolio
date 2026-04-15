-- mart_tag_activity
-- Grain: one row per tag within the staging window.
--
-- Aggregates question volume, engagement, and resolution metrics by tag.
-- Only includes tags that appear in at least 10 questions within the window
-- to filter out noise from rarely-used tags.
--
-- Joined with the tags reference table to enrich with the overall
-- question_count from the source (full historical count, not window-scoped).

with tag_questions as (

    select * from {{ ref('int_question_tag_exploded') }}

),

tags_ref as (

    select
        tag_name,
        question_count      as total_historical_question_count
    from {{ ref('stg_stackoverflow__tags') }}

),

tag_agg as (

    select
        tag_name,
        count(distinct question_id)                                         as questions_in_window,
        sum(case when has_accepted_answer then 1 else 0 end)                as questions_with_accepted_answer,
        sum(case when is_unanswered then 1 else 0 end)                      as unanswered_questions,
        round(avg(question_score), 2)                                       as avg_question_score,
        round(avg(view_count), 0)                                           as avg_view_count,
        round(avg(answer_count), 2)                                         as avg_answer_count,
        round(
            100.0 * sum(case when has_accepted_answer then 1 else 0 end)
            / nullif(count(distinct question_id), 0),
            2
        )                                                                   as accepted_answer_rate_pct,
        round(
            100.0 * sum(case when is_unanswered then 1 else 0 end)
            / nullif(count(distinct question_id), 0),
            2
        )                                                                   as unanswered_rate_pct
    from tag_questions
    group by tag_name
    having count(distinct question_id) >= 10

)

select
    ta.tag_name,
    ta.questions_in_window,
    ta.questions_with_accepted_answer,
    ta.unanswered_questions,
    ta.avg_question_score,
    ta.avg_view_count,
    ta.avg_answer_count,
    ta.accepted_answer_rate_pct,
    ta.unanswered_rate_pct,
    ref.total_historical_question_count
from tag_agg ta
left join tags_ref ref
    on ta.tag_name = ref.tag_name
order by
    ta.questions_in_window desc
