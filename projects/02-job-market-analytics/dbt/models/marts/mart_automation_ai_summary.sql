with enriched as (

    select * from {{ ref('int_job_market_enriched') }}

)

select
    automation_risk,
    ai_adoption_level,
    count(*) as total_records,
    avg(salary_usd) as average_salary_usd,
    {{ job_market_median('salary_usd') }} as median_salary_usd,
    avg(cast(is_remote_friendly as integer)) as remote_friendly_share,
    avg(cast(is_growth_projection as integer)) as growth_projection_share
from enriched
group by 1, 2
