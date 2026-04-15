-- assert_mart_monthly_positive_counts
-- Singular test: verify that every month in the monthly activity mart has at
-- least one question and that key rate columns are within expected bounds.
--
-- Returns rows that violate any of these invariants (should return 0 rows).

select
    month_start,
    total_questions,
    unanswered_rate_pct,
    accepted_answer_rate_pct
from {{ ref('mart_monthly_question_activity') }}
where
    -- Every month must have at least 1 question
    total_questions < 1
    -- Rates must be between 0 and 100
    or unanswered_rate_pct < 0
    or unanswered_rate_pct > 100
    or accepted_answer_rate_pct < 0
    or accepted_answer_rate_pct > 100
    -- Rates cannot both be > 100 when summed (sanity check)
    or (unanswered_rate_pct + accepted_answer_rate_pct) > 100
