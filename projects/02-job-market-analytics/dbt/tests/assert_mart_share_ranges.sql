select *
from (
    select 'mart_job_title_summary' as mart_name, remote_friendly_share as share_value from {{ ref('mart_job_title_summary') }}
    union all
    select 'mart_job_title_summary' as mart_name, high_automation_risk_share as share_value from {{ ref('mart_job_title_summary') }}
    union all
    select 'mart_job_title_summary' as mart_name, high_ai_adoption_share as share_value from {{ ref('mart_job_title_summary') }}
    union all
    select 'mart_job_title_summary' as mart_name, growth_projection_share as share_value from {{ ref('mart_job_title_summary') }}
    union all
    select 'mart_industry_summary' as mart_name, remote_friendly_share as share_value from {{ ref('mart_industry_summary') }}
    union all
    select 'mart_industry_summary' as mart_name, high_automation_risk_share as share_value from {{ ref('mart_industry_summary') }}
    union all
    select 'mart_industry_summary' as mart_name, high_ai_adoption_share as share_value from {{ ref('mart_industry_summary') }}
    union all
    select 'mart_industry_summary' as mart_name, growth_projection_share as share_value from {{ ref('mart_industry_summary') }}
    union all
    select 'mart_location_summary' as mart_name, remote_friendly_share as share_value from {{ ref('mart_location_summary') }}
    union all
    select 'mart_location_summary' as mart_name, high_automation_risk_share as share_value from {{ ref('mart_location_summary') }}
    union all
    select 'mart_location_summary' as mart_name, high_ai_adoption_share as share_value from {{ ref('mart_location_summary') }}
    union all
    select 'mart_location_summary' as mart_name, growth_projection_share as share_value from {{ ref('mart_location_summary') }}
    union all
    select 'mart_automation_ai_summary' as mart_name, remote_friendly_share as share_value from {{ ref('mart_automation_ai_summary') }}
    union all
    select 'mart_automation_ai_summary' as mart_name, growth_projection_share as share_value from {{ ref('mart_automation_ai_summary') }}
) shares
where share_value < 0
   or share_value > 1
   or share_value is null
