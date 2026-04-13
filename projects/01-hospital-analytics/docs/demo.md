# Demo / Run Guide

Concise local run flow for the hospital analytics portfolio case.

This guide assumes the repository is already cloned, the Python environment exists, Node.js is installed, and local PostgreSQL credentials are configured in:

```text
projects/01-hospital-analytics/.env
```

Use `.env.example` as the template for required PostgreSQL settings.

## 1. Activate the Python Environment

From the repository root:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell execution policy blocks activation, use the virtual environment Python executable directly in the commands below:

```powershell
.\.venv\Scripts\python.exe <script-path>
```

## 2. Refresh Pipeline Outputs if Needed

If the Bronze, Silver, and Gold artifacts already exist, you can skip directly to the serving job. To rebuild the local medallion artifacts from the repository root:

```powershell
python projects/01-hospital-analytics/src/jobs/run_ingestion.py
python projects/01-hospital-analytics/src/jobs/run_bronze.py
python projects/01-hospital-analytics/src/jobs/run_silver.py
python projects/01-hospital-analytics/src/jobs/run_gold.py
```

For a faster demo refresh when Gold files already exist:

```powershell
python projects/01-hospital-analytics/src/jobs/run_gold.py
```

## 3. Load PostgreSQL Serving Views

Make sure local PostgreSQL is running and the database credentials in `.env` are valid. Then run:

```powershell
python projects/01-hospital-analytics/src/jobs/run_serving.py
```

This loads Gold outputs into the `analytics` schema and creates serving views in the `serving` schema.

## 4. Start the Flask API

From the repository root:

```powershell
python projects/01-hospital-analytics/api/app.py
```

The default local API URL is:

```text
http://127.0.0.1:5000
```

Keep this terminal running while using the dashboard.

## 5. Start the Dashboard

Open a second terminal and run:

```powershell
cd projects/01-hospital-analytics/dashboard
if (!(Test-Path .env)) { Copy-Item .env.example .env }
npm install
npm run dev
```

The dashboard reads the API base URL from:

```text
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Vite will print the local dashboard URL, usually:

```text
http://localhost:5173
```

## 6. Validate the API

Optional browser or PowerShell checks:

```powershell
Invoke-RestMethod http://127.0.0.1:5000/health
Invoke-RestMethod http://127.0.0.1:5000/api/v1/kpis
Invoke-RestMethod "http://127.0.0.1:5000/api/v1/daily-patient-flow?order_by=admission_date&limit=10"
Invoke-RestMethod http://127.0.0.1:5000/api/v1/department-referrals
Invoke-RestMethod http://127.0.0.1:5000/api/v1/demographics
```

## Expected Demo Flow

For reviewers, the important path is:

```text
Gold CSV outputs -> PostgreSQL serving views -> Flask API -> React dashboard
```

Earlier ingestion, Bronze, and Silver steps are available for a fuller walkthrough, but they do not need to be rerun for every dashboard demo if the local artifacts are already present.
