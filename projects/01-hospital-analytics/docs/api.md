# API Layer - Flask

The Flask API exposes the hospital analytics PostgreSQL serving views for future
dashboard consumption.

The API reads from the `serving` schema instead of local CSV files or earlier
medallion layers. This keeps the service boundary simple: Bronze, Silver, Gold,
and PostgreSQL loading remain owned by pipeline jobs, while the API only serves
already-curated analytical outputs.

## Source Views

The API queries only these PostgreSQL views:

- `serving.v_dashboard_kpis`
- `serving.v_daily_patient_flow`
- `serving.v_department_referral_summary`
- `serving.v_demographic_summary`

It does not read from raw CSV files, Bronze, Silver, Gold CSV artifacts, or the
physical `analytics` tables directly.

## Endpoints

### `GET /health`

Returns a simple service health response.

```json
{
  "data": {
    "service": "hospital-analytics-api",
    "status": "ok"
  }
}
```

### `GET /api/v1/kpis`

Returns the single-row result from `serving.v_dashboard_kpis`.

```json
{
  "data": {
    "total_patient_events": 1000,
    "average_waittime_overall": 35.2,
    "average_satisfaction_overall": 4.1,
    "number_of_daily_points": 30,
    "number_of_department_groups": 8,
    "number_of_demographic_groups": 40
  }
}
```

### `GET /api/v1/daily-patient-flow`

Returns rows from `serving.v_daily_patient_flow`.

```json
{
  "data": [
    {
      "admission_date": "2025-01-01",
      "total_patient_events": 42,
      "average_patient_waittime": 31.4,
      "average_patient_satisfaction_score": 4.2,
      "admitted_patient_events": 20,
      "null_department_referral_events": 3,
      "null_satisfaction_score_events": 1
    }
  ]
}
```

### `GET /api/v1/department-referrals`

Returns rows from `serving.v_department_referral_summary`.

```json
{
  "data": [
    {
      "department_referral": "General Practice",
      "total_patient_events": 250,
      "average_patient_waittime": 28.9,
      "average_patient_satisfaction_score": 4.0,
      "share_of_total_events": 0.25
    }
  ]
}
```

### `GET /api/v1/demographics`

Returns rows from `serving.v_demographic_summary`.

```json
{
  "data": [
    {
      "patient_gender": "F",
      "patient_race": "White",
      "patient_age_band": "36_50",
      "total_patient_events": 80,
      "average_patient_waittime": 30.5,
      "average_patient_satisfaction_score": 4.3
    }
  ]
}
```

## Query Parameters

The list endpoints support optional, safe query parameters:

- `limit`: integer from `1` to `1000`
- `order_by`: whitelisted column for that endpoint's serving view

Example:

```text
http://127.0.0.1:5000/api/v1/daily-patient-flow?order_by=admission_date&limit=50
```

The API does not concatenate raw user input into SQL. Ordering is allowed only
for known serving-view columns, and the SQL identifiers are built with
`psycopg.sql`.

## How to Run Locally

From the repository root, install Flask if it is not already available in your
virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pip install Flask
```

Make sure the PostgreSQL serving stage has already been run:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/src/jobs/run_serving.py
```

Start the API:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/api/app.py
```

If your virtual environment is already activated:

```powershell
python projects/01-hospital-analytics/api/app.py
```

By default, the API runs at:

```text
http://127.0.0.1:5000
```

The API reads PostgreSQL settings from:

```text
projects/01-hospital-analytics/.env
```

Optional local API settings can also be added to that file:

```text
API_SERVICE_NAME=hospital-analytics-api
API_HOST=127.0.0.1
API_PORT=5000
API_DEBUG=false
```

## Error Handling

Database failures return JSON with a `503` status code and a generic error
message. Stack traces are logged locally but are not returned in HTTP responses.

Invalid query parameters return JSON with a `400` status code.

## CORS

The API adds simple local-development CORS headers for `GET` and `OPTIONS`
requests so a future dashboard can call it from another local origin.

## Out of Scope

This API layer does not:

- Rebuild Bronze, Silver, Gold, or serving logic.
- Read directly from CSV files.
- Read directly from Bronze, Silver, Gold, or physical `analytics` tables.
- Add authentication.
- Add dashboard or frontend code.
- Add Docker, CI/CD, Terraform, or deployment tooling.
- Introduce DBT or Spark.
