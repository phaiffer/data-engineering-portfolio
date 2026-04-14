# Silver v1 Plan

Silver v1 standardizes the raw Kaggle job-market extract into cleaner, row-preserving analytical records. It is not the final dimensional model.

## Grain Assumption

One row represents one source job-market insight record from the selected Bronze CSV.

This is an assumption based on the current raw file shape. The dataset does not expose a natural primary key or posting timestamp, so Silver does not claim job-posting uniqueness.

## Raw Columns

- `Job_Title`
- `Industry`
- `Company_Size`
- `Location`
- `AI_Adoption_Level`
- `Automation_Risk`
- `Required_Skills`
- `Salary_USD`
- `Remote_Friendly`
- `Job_Growth_Projection`

Bronze profiling reported 500 rows, 10 columns, no nulls, and no duplicate rows in the selected CSV.

## Silver Rename Map

| Raw column | Silver column |
| --- | --- |
| `Job_Title` | `job_title` |
| `Industry` | `industry` |
| `Company_Size` | `company_size` |
| `Location` | `location` |
| `AI_Adoption_Level` | `ai_adoption_level` |
| `Automation_Risk` | `automation_risk` |
| `Required_Skills` | `required_skills` |
| `Salary_USD` | `salary_usd` |
| `Remote_Friendly` | `remote_friendly` |
| `Job_Growth_Projection` | `job_growth_projection` |

## Type Strategy

- Keep categorical fields as nullable strings.
- Convert `salary_usd` with `pandas.to_numeric(errors="coerce")`.
- Do not add dates because the source does not include date-like fields.

## Null Handling

- Trim whitespace in string fields.
- Convert blank strings to nulls.
- Preserve source rows even if conversions create nulls.
- Report null counts in Silver metadata instead of dropping records.

## Normalization

Silver normalizes obvious categorical values into lowercase analytical tokens:

- `AI Researcher` -> `ai_researcher`
- `San Francisco` -> `san_francisco`
- `UX/UI Design` -> `ux_ui_design`
- `Yes` / `No` -> `yes` / `no`

This creates stable values for future DBT staging and dimensions without inventing new business categories.

## Silver Will Do

- Load the Bronze-selected CSV from Bronze metadata.
- Preserve row count.
- Rename columns to `snake_case`.
- Trim string fields and convert blank strings to nulls.
- Safely cast `salary_usd` to numeric.
- Normalize categorical values consistently.
- Write a Silver CSV and Silver metadata JSON.
- Report duplicate row count and null counts.

## Silver Will Not Do Yet

- Deduplicate rows.
- Aggregate records.
- Create dimensional tables.
- Create Gold marts or KPIs.
- Create DBT models beyond the existing scaffold.
- Infer unsupported semantics such as job posting identity, freshness, or market representativeness.

## Open Semantic Questions

- Does each row represent a synthetic job-market scenario, a job posting, or an aggregated market insight?
- Should `remote_friendly` become a boolean in future marts, or remain a categorical dimension?
- Should `salary_usd` be modeled as exact salary, simulated salary, or approximate compensation?
- Are `job_growth_projection`, `automation_risk`, and `ai_adoption_level` ordinal categories in the source methodology, or only labels?

## DBT and Gold Preparation

Silver v1 produces stable column names and normalized category values. This prepares future DBT work for:

- staging models over a consistent row-level input;
- accepted-value tests for compact categorical fields;
- intermediate models for salary bands and categorical dimensions;
- Gold marts for role, industry, location, AI adoption, automation risk, and growth projection analysis.
