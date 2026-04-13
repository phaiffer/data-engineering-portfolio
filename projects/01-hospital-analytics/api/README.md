# Hospital Analytics API

This directory contains the first lightweight Flask API for exposing the
PostgreSQL serving views used by future dashboards.

Run it from the repository root:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/api/app.py
```

If your virtual environment is already activated:

```powershell
python projects/01-hospital-analytics/api/app.py
```

The API reads PostgreSQL connection settings from:

```text
projects/01-hospital-analytics/.env
```

Detailed endpoint documentation lives in:

```text
projects/01-hospital-analytics/docs/api.md
```
