-- assert_reputation_tier_coverage
-- Singular test: verify that mart_user_reputation_segments contains all five
-- expected tiers. If any tier is missing, the mart has a data quality gap.
--
-- Stability note:
--   This test is reliable for the default year window (2021-present, ~4 years).
--   All five tiers have meaningful user populations over any multi-year window.
--   For very narrow windows (e.g., a single month via stackoverflow_min_year=2024)
--   the 'expert' tier might theoretically be absent if no expert-reputation user
--   asked a question in that window. In practice this does not occur for windows
--   >= 6 months, but if you reduce the year window significantly and this test
--   fails, the fix is to widen the window rather than relax the test.
--
-- Bug note:
--   The alias `at` is a reserved keyword in BigQuery SQL and would cause a parse
--   error. The alias is named `actual` here instead.
--
-- Returns the missing tier names (should return 0 rows).

with expected_tiers as (

    select tier
    from unnest(['new', 'contributor', 'established', 'advanced', 'expert']) as tier

),

actual_tiers as (

    select reputation_tier
    from {{ ref('mart_user_reputation_segments') }}

)

select expected_tiers.tier as missing_tier
from expected_tiers
left join actual_tiers
    on expected_tiers.tier = actual_tiers.reputation_tier
where actual_tiers.reputation_tier is null
