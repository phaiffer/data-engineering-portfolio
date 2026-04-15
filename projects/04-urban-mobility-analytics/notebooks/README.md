# Notebooks

This folder is for lightweight exploratory validation only.

Rules for this project:

- notebooks should validate source assumptions and landed data;
- reusable pipeline logic belongs in `src/`, not in notebooks;
- notebook cells may import helper functions from `src/`;
- notebooks should stay small and honest.

Environment notes:

- run notebooks with the project-compatible environment from `projects/04-urban-mobility-analytics/requirements.txt`;
- the preferred notebook path is Pandas with `pyarrow`;
- if `pyarrow` is missing but `duckdb` is available, the notebook falls back to DuckDB for Parquet inspection;
- `ipykernel` is included in the project requirements so the environment can be registered as a kernel;
- the notebook bootstrap supports three launch locations: repository root, project root, and this `notebooks/` directory.
