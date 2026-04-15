# Documentation Index

Curated documentation for the retail revenue analytics case study.

- [Bronze layer](bronze.md): current raw ingestion, inventory, profiling behavior, and scope notes.
- [Source tables](source_tables.md): raw Olist files, business roles, likely grains, joins, and Silver v1 scope.
- [Silver plan](silver_plan.md): source-aligned Silver strategy and deferred tables.
- [Silver layer](silver.md): implemented Silver outputs, metadata, and run command.
- [Modeling plan](modeling_plan.md): likely future fact and dimension direction.
- [Gold layer](gold.md): Gold v1 outputs, KPI definitions, and limitations.
- [DBT layer](dbt.md): DuckDB DBT project, source strategy, model layers, and tests.
- [Dimensional marts](marts.md): dimensions, fact-like mart, business marts, grains, and caveats.
- [API layer](api.md): read-only Flask API over DuckDB marts, endpoints, filters, and limitations.
- [Project README](../README.md): case study purpose, dataset choice, architecture direction, and run commands.

Future documentation should be added only when the corresponding implementation exists.
