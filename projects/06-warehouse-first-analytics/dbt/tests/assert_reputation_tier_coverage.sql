-- assert_reputation_tier_coverage
-- Singular test: verify that mart_user_reputation_segments contains all five
-- expected tiers. If any tier is missing, the mart has a data quality gap
-- (e.g., no users in that tier asked questions in the staging window, which
-- would be unexpected for any multi-year window).
--
-- Returns the missing tier names (should return 0 rows).

with expected_tiers as (

    select tier from unnest(['new', 'contributor', 'established', 'advanced', 'expert']) as tier

),

actual_tiers as (

    select reputation_tier from {{ ref('mart_user_reputation_segments') }}

)

select et.tier as missing_tier
from expected_tiers et
left join actual_tiers at
    on et.tier = at.reputation_tier
where at.reputation_tier is null
