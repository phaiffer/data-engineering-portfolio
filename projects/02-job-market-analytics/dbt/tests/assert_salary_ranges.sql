select *
from {{ ref('stg_job_market_insights') }}
where salary_usd <= 0
