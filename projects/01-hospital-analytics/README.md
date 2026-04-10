# Hospital Analytics

Foundational scaffold for a hospital-focused data engineering project built as an end-to-end portfolio case.

## Objective

Create a structured data pipeline project for hospital analytics use cases, with clear separation between ingestion, medallion-layer processing, data quality, modeling, and future data serving.

## Domain Focus

The project is intended for hospital analytics scenarios such as operational reporting, curated analytical datasets, and downstream consumption patterns. Specific datasets, schemas, and transformations will be defined later.

## Medallion Layers

- `bronze`: raw landed and minimally standardized data assets
- `silver`: cleaned and conformed intermediate datasets
- `gold`: curated analytical outputs for consumption

## Planned Stack

- Python
- PySpark
- Pandas
- NumPy
- DBT
- Databricks
- Flask API later for curated data access

## Folder Overview

- `data/`: local layer-oriented storage placeholders
- `src/`: ingestion, processing, jobs, quality, and utility modules
- `dbt/`: transformation modeling scaffold aligned to medallion stages
- `docs/`: project-specific documentation
- `tests/`: unit and integration test areas
- `notebooks/`: exploratory and validation notebooks
- `api/`: reserved for future service exposure

## Status

This project currently contains structure only. ETL logic, data contracts, DBT models, API implementation, and dashboards will be added in later iterations.
