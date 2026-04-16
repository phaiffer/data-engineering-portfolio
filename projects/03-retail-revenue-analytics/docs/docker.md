# Docker Packaging

Docker was added to make the retail revenue analytics case easier to demo, easier to test in a container, and easier to run without redoing the API and dashboard setup by hand every time.

This is still a local-first packaging layer. It is not a production container platform.
Manual local development remains an official path. Docker is included for demo ergonomics and reproducibility, not as a requirement for everyday project work.

## What Docker Improves

- repeatable local startup for the Flask API;
- repeatable local startup for the dashboard;
- one Compose file for the demo path;
- an optional pipeline container for explicit tests, Python jobs, and DBT commands.

## What Docker Does Not Change

- the analytical contracts stay the same;
- DBT still reads the local Silver outputs and writes the local DuckDB mart database;
- the API stays read-only;
- the dashboard stays a browser-based local presentation layer;
- `docker compose up` does not automatically download Kaggle data or rebuild the analytical stack.

## Containerized Services

### retail-api

- Builds from `docker/api.Dockerfile`.
- Runs the Flask API on port `5002`.
- Reads the DuckDB mart database through a bind mount of `./data`.

### retail-dashboard

- Builds from `docker/dashboard.Dockerfile`.
- Creates a static dashboard build and serves it on port `4173`.
- Uses a browser-facing API base URL baked into the build with `VITE_API_BASE_URL`.

### retail-pipeline

- Builds from `docker/pipeline.Dockerfile`.
- Exists for explicit test, job, and DBT commands only.
- Is placed behind the Compose profile `pipeline` so it does not start during the normal demo path.
- On Linux, can run with the host UID and GID so bind-mounted DBT artifacts are not written as `root`.

## Data Preparation

The API container expects the DuckDB mart database at:

```text
projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

Inside the containers, that same file is mounted at:

```text
/workspace/projects/03-retail-revenue-analytics/data/retail_revenue_analytics.duckdb
```

If the DuckDB file does not exist yet, the API still starts, but `/health` will report a degraded state and the data endpoints will not return modeled results.

## Run The Demo Stack

From the project directory:

```bash
cd projects/03-retail-revenue-analytics
docker compose up --build retail-api retail-dashboard
```

Expected host URLs:

```text
API:       http://127.0.0.1:5002
Dashboard: http://127.0.0.1:4173
```

The dashboard build uses `http://127.0.0.1:5002` as the default browser-facing API URL. That is intentional: the browser runs on the host machine, so it needs a host-reachable API URL rather than a Docker-internal hostname.

## Change The Dashboard API URL

If you need a different browser-facing API URL, rebuild the dashboard image with a different Compose build argument source:

```bash
cd projects/03-retail-revenue-analytics
RETAIL_REVENUE_DASHBOARD_API_BASE_URL=http://127.0.0.1:5002 docker compose build retail-dashboard
docker compose up retail-dashboard
```

## Optional Pipeline Container

Use the pipeline container for explicit tests and jobs only.

Windows PowerShell examples:

```powershell
Set-Location .\projects\03-retail-revenue-analytics
docker compose --profile pipeline run --rm retail-pipeline python -m pytest tests
docker compose --profile pipeline run --rm retail-pipeline sh -lc "cd dbt && python -m dbt.cli.main build --profiles-dir . --target duckdb"
docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_silver.py
```

On Linux, pass your host UID and GID when you run the pipeline service:

```bash
cd projects/03-retail-revenue-analytics
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_bronze.py
```

Use `HOST_UID` and `HOST_GID` in these commands. `UID` is a readonly variable in `bash`, so the `HOST_*` names keep the Linux shell experience predictable.

Python job examples:

```bash
cd projects/03-retail-revenue-analytics
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_bronze.py
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_silver.py
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline python src/jobs/run_gold.py
```

DBT examples:

```bash
cd projects/03-retail-revenue-analytics
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline sh -lc "cd dbt && python -m dbt.cli.main debug --profiles-dir . --target duckdb"
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline sh -lc "cd dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb"
HOST_UID=$(id -u) HOST_GID=$(id -g) docker compose --profile pipeline run --rm retail-pipeline sh -lc "cd dbt && python -m dbt.cli.main test --profiles-dir . --target duckdb"
```

If you want to run ingestion in the pipeline container, provide the same Kaggle credentials you would use locally through environment variables such as `KAGGLE_USERNAME` and `KAGGLE_KEY`.

## Generated DBT Artifacts

`dbt/logs/` and `dbt/target/` are generated local artifacts. They are expected to change during DBT runs, and they are safe to remove and recreate if you need a clean local state.

The pipeline service is mapped to the host user on Linux through `HOST_UID` and `HOST_GID` so normal container runs do not leave those bind-mounted folders owned by `root`.

## Linux Permission Recovery

If a previous Docker run already created root-owned DBT artifacts, fix the ownership from the project directory:

```bash
cd projects/03-retail-revenue-analytics
sudo chown -R "$USER":"$(id -gn)" dbt/logs dbt/target
```

If you would rather reset them completely:

```bash
cd projects/03-retail-revenue-analytics
sudo rm -rf dbt/logs dbt/target
mkdir -p dbt/logs dbt/target
```

## Practical Scope

This Docker setup is meant to improve:

- demo ergonomics;
- portability across local Linux environments;
- separation between generated data and container images;
- repeatability for API and dashboard startup.

It is not claiming:

- production hardening;
- cloud deployment;
- orchestration;
- auth or multi-user behavior;
- automated data refresh on container startup.
