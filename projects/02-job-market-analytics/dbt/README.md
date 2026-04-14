# DBT Scaffold

This directory is a DBT-oriented scaffold for the job market analytics project.

The current implementation is Bronze-first and does not yet publish production DBT marts. The scaffold exists to make the intended modeling path explicit without overclaiming what has been built.

## Intended Direction

Future DBT work should evolve toward:

- `bronze`: source declarations or external table references over raw landed data, once a serving warehouse is selected;
- `silver`: cleaned and typed job-market records with stable naming and documented grain;
- `gold`: analytical marts for job-role, industry, automation exposure, salary, company-size, and location analysis where those dimensions are supported by source columns.

## Current Status

- `dbt_project.yml` is present as a project scaffold.
- Model folders exist for Bronze, Silver, and Gold.
- Placeholder SQL files are intentionally non-production markers.

Do not treat this directory as a completed DBT implementation yet.
