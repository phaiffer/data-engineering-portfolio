select *
from (
    select 'mart_job_title_summary' as mart_name, job_title as grain_value, total_records
    from {{ ref('mart_job_title_summary') }}

    union all

    select 'mart_industry_summary' as mart_name, industry as grain_value, total_records
    from {{ ref('mart_industry_summary') }}

    union all

    select 'mart_location_summary' as mart_name, location as grain_value, total_records
    from {{ ref('mart_location_summary') }}

    union all

    select
        'mart_automation_ai_summary' as mart_name,
        automation_risk || '-' || ai_adoption_level as grain_value,
        total_records
    from {{ ref('mart_automation_ai_summary') }}
) mart_counts
where total_records <= 0
