-- assert_tag_activity_min_question_count
-- Singular test: verify that mart_tag_activity only contains tags with
-- at least 10 questions in the window, as defined by the mart's HAVING clause.
--
-- Returns rows that violate this invariant (should return 0 rows).

select
    tag_name,
    questions_in_window
from {{ ref('mart_tag_activity') }}
where questions_in_window < 10
