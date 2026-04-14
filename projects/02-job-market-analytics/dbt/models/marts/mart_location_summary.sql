with enriched as (

    select * from {{ ref('int_job_market_enriched') }}

)

select
    location,
    count(*) as total_records,
    avg(salary_usd) as average_salary_usd,
    {{ job_market_median('salary_usd') }} as median_salary_usd,
    min(salary_usd) as min_salary_usd,
    max(salary_usd) as max_salary_usd,
    avg(cast(is_remote_friendly as integer)) as remote_friendly_share,
    avg(cast(is_high_automation_risk as integer)) as high_automation_risk_share,
    avg(cast(is_high_ai_adoption as integer)) as high_ai_adoption_share,
    avg(cast(is_growth_projection as integer)) as growth_projection_share
from enriched
group by 1
