# notebooks

Lightweight validation and exploration notebooks for the warehouse-first analytics project.

| Notebook | Purpose |
|---|---|
| [01_source_validation.ipynb](01_source_validation.ipynb) | Inspect source schema, sample rows, and validate key columns before modeling |

## Usage

```bash
cd projects/06-warehouse-first-analytics/
source .venv/bin/activate
pip install -r requirements.txt
jupyter notebook notebooks/01_source_validation.ipynb
```

## Notes

- Notebooks require a valid GCP authentication context (run `gcloud auth application-default login` first).
- They are exploratory only — no reusable modeling logic lives here.
- Set `GCP_PROJECT_ID` and `STACKOVERFLOW_MIN_YEAR` in `.env` before running.
