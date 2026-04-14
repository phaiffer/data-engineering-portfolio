with staged as (

    select * from {{ ref('stg_job_market_insights') }}

)

select
    job_title,
    industry,
    company_size,
    location,
    ai_adoption_level,
    automation_risk,
    required_skills,
    salary_usd,
    remote_friendly,
    job_growth_projection,
    remote_friendly = 'yes' as is_remote_friendly,
    automation_risk = 'high' as is_high_automation_risk,
    ai_adoption_level = 'high' as is_high_ai_adoption,
    job_growth_projection = 'growth' as is_growth_projection
from staged
