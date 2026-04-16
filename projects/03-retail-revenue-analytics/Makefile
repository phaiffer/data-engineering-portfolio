.PHONY: silver gold dbt-debug dbt-run dbt-test test dashboard-install dashboard-build

silver:
	python src/jobs/run_silver.py

gold:
	python src/jobs/run_gold.py

dbt-debug:
	cd dbt && python -m dbt.cli.main debug --profiles-dir . --target duckdb

dbt-run:
	cd dbt && python -m dbt.cli.main run --profiles-dir . --target duckdb

dbt-test:
	cd dbt && python -m dbt.cli.main test --profiles-dir . --target duckdb

test:
	python -m pytest tests

dashboard-install:
	cd dashboard && npm install

dashboard-build:
	cd dashboard && npm run build
