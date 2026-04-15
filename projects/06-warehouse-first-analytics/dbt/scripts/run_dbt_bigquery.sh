#!/usr/bin/env bash
# run_dbt_bigquery.sh
# Convenience wrapper for running dbt against BigQuery.
# Run from the dbt/ directory:   bash scripts/run_dbt_bigquery.sh
# Or from project root:          bash dbt/scripts/run_dbt_bigquery.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DBT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${DBT_DIR}"

echo "==> Working directory: ${DBT_DIR}"
echo "==> dbt version: $(dbt --version 2>&1 | head -1)"
echo ""

# Step 1: validate connection and profile
echo "--- dbt debug ---"
dbt debug

# Step 2: install packages (dbt_utils)
echo ""
echo "--- dbt deps ---"
dbt deps

# Step 3: run all models
echo ""
echo "--- dbt run ---"
dbt run

# Step 4: run all tests
echo ""
echo "--- dbt test ---"
dbt test

# Step 5: optional docs (comment out if not needed)
# echo ""
# echo "--- dbt docs generate ---"
# dbt docs generate

echo ""
echo "==> Done. All models built and tested."
