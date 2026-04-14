{% macro job_market_float_type() -%}
    {%- if target.type == 'postgres' -%}
        double precision
    {%- else -%}
        double
    {%- endif -%}
{%- endmacro %}

{% macro job_market_median(column_name) -%}
    {%- if target.type == 'postgres' -%}
        percentile_cont(0.5) within group (order by {{ column_name }})
    {%- else -%}
        median({{ column_name }})
    {%- endif -%}
{%- endmacro %}
