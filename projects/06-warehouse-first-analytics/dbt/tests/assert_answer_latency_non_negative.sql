-- assert_answer_latency_non_negative
-- Singular test: verify that no answered question has a negative latency value.
--
-- A negative hours_to_first_answer would indicate a data quality issue in the
-- source (answer created_at before question created_at), which can occasionally
-- occur due to clock skew or data pipeline issues in the public dataset.
--
-- This test returns rows that violate the invariant (i.e., it should return 0 rows).

select
    question_id,
    question_created_at,
    hours_to_first_answer,
    hours_to_accepted_answer
from {{ ref('int_questions_with_answers') }}
where
    hours_to_first_answer < 0
    or hours_to_accepted_answer < 0
