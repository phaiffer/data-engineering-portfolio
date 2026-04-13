# Hospital Analytics Dashboard

React, Vite, and TypeScript dashboard for the hospital analytics portfolio case.
It consumes the Flask API over PostgreSQL serving views and presents the first
frontend layer for the project.

## Purpose

This dashboard demonstrates the curated analytical outputs produced by the
pipeline:

1. Kaggle raw data is landed and profiled in Bronze.
2. Silver processing cleans and conforms patient-flow records.
3. Gold processing creates dashboard-ready analytical outputs.
4. The PostgreSQL serving job loads curated tables and views.
5. The Flask API exposes serving views over HTTP.
6. This dashboard consumes the API and visualizes the results.

The frontend does not read CSV files or rebuild medallion-layer logic.

## Required API Endpoints

The dashboard expects the Flask API to expose:

- `GET /health`
- `GET /api/v1/kpis`
- `GET /api/v1/daily-patient-flow`
- `GET /api/v1/department-referrals`
- `GET /api/v1/demographics`

By default, the local API runs at:

```text
http://127.0.0.1:5000
```

## Environment Variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Set the API base URL:

```text
VITE_API_BASE_URL=http://127.0.0.1:5000
```

Do not commit local `.env` files.

## Install Dependencies

From this directory:

```powershell
npm install
```

## Run Locally

Start the Flask API from the repository root:

```powershell
.\.venv\Scripts\python.exe projects/01-hospital-analytics/api/app.py
```

Then start the dashboard:

```powershell
npm run dev
```

Vite will print the local dashboard URL, usually:

```text
http://localhost:5173
```

## Build

```powershell
npm run build
```

The production build is emitted to `dist/`, which is ignored by Git.
