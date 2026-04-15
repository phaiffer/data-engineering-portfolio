# Notebooks

Notebooks in this project are exploratory only.

Use notebooks to inspect landed raw files, validate assumptions, and understand source columns. Reusable ingestion, inventory, profiling, and transformation logic belongs under `src/` so it can be executed from jobs and tested later.

Current notebook:

- `01_dataset_profiling.ipynb`: lightweight exploration of the Olist raw landing area and the Bronze-selected CSV.
- `02_silver_validation.ipynb`: lightweight validation of source-aligned Silver CSV outputs.
- `03_gold_output_validation.ipynb`: lightweight validation of Gold v1 analytical outputs and simple revenue sanity checks.
