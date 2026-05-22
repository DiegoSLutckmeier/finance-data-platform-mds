# Local Setup

## Python Environment

The project has been tested with the local `sparkenv` environment:

```bash
/Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/python
```

Install Python dependencies:

```bash
/Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/python -m pip install -r requirements.txt
```

## Environment Variables

Create a local `.env` file from `.env.example` and set your Stripe test API key.

```text
STRIPE_API_KEY=sk_test_xxx
LAKEHOUSE_DATA_DIR=./data
STRIPE_STATE_PATH=./data/state/stripe_state.json
DUCKDB_PATH=./data/finance_lakehouse.duckdb
```

The `.env` file is ignored by Git because it can contain secrets.

## Manual Pipeline

Run extraction:

```bash
/Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/python scripts/extract_all.py
```

Validate Bronze files:

```bash
/Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/python scripts/validate_bronze.py
```

Create DuckDB Bronze views:

```bash
/Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/python scripts/create_duckdb_bronze_views.py
```

Run dbt:

```bash
cd dbt_finance_platform
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt run
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt test
```

## dbt Documentation

dbt can generate a local documentation website with model descriptions, source definitions, columns, tests, and lineage.

From the dbt project folder:

```bash
cd /Users/diegolutckmeier/Developer/Projects/finance-data-platform-mds/dbt_finance_platform
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt docs generate
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt docs serve --port 8082
```

Then open:

```text
http://localhost:8082
```

Port `8082` is used here to avoid conflict with Airflow, which usually runs on port `8080`.

