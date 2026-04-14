with source as (

    select * from {{ source('local_silver', 'ai_job_market_insights_silver') }}

)

select
    cast(job_title as varchar) as job_title,
    cast(industry as varchar) as industry,
    cast(company_size as varchar) as company_size,
    cast(location as varchar) as location,
    cast(ai_adoption_level as varchar) as ai_adoption_level,
    cast(automation_risk as varchar) as automation_risk,
    cast(required_skills as varchar) as required_skills,
    cast(salary_usd as double) as salary_usd,
    case
        when lower(cast(remote_friendly as varchar)) in ('yes', 'true', '1') then 'yes'
        when lower(cast(remote_friendly as varchar)) in ('no', 'false', '0') then 'no'
        else lower(cast(remote_friendly as varchar))
    end as remote_friendly,
    cast(job_growth_projection as varchar) as job_growth_projection
from source
