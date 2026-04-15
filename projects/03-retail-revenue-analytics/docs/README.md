# Documentation Index

Curated documentation for the retail revenue analytics case study.

Official run guidance lives in:

- [Project README](../README.md): manual local path, quick demo path, troubleshooting, and Docker-assisted demo path.
- [Docker packaging](docker.md): container-specific setup, mounted DuckDB path, and Linux permission guidance for the optional pipeline container.

- [Bronze layer](bronze.md): current raw ingestion, inventory, profiling behavior, and scope notes.
- [Source tables](source_tables.md): raw Olist files, business roles, likely grains, joins, and Silver v1 scope.
- [Silver plan](silver_plan.md): source-aligned Silver strategy and deferred tables.
- [Silver layer](silver.md): implemented Silver outputs, metadata, and run command.
- [Modeling plan](modeling_plan.md): likely future fact and dimension direction.
- [Gold layer](gold.md): Gold v1 outputs, KPI definitions, and limitations.
- [DBT layer](dbt.md): DuckDB DBT project, source strategy, model layers, and tests.
- [Dimensional marts](marts.md): dimensions, fact-like mart, business marts, grains, and caveats.
- [API layer](api.md): read-only Flask API over DuckDB marts, endpoints, filters, and limitations.
- [Dashboard layer](dashboard.md): local React dashboard over the API, sections, KPI caveats, and non-goals.
- [Docker packaging](docker.md): API and dashboard containers, Compose demo path, mounted DuckDB data, and optional pipeline container usage.
- [Project README](../README.md): case study purpose, dataset choice, architecture direction, official run paths, and troubleshooting.

Future documentation should be added only when the corresponding implementation exists.
