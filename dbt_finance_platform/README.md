# dbt Finance Platform

This dbt project transforms local Stripe Bronze views in DuckDB into Silver staging models and Gold analytics marts.

## Layers

- `models/staging`: Silver models. These clean, type, and deduplicate Stripe objects from Bronze.
- `models/marts`: Gold models. These shape Silver data into analytics-ready tables.

## Run

From this folder:

```bash
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt run
DBT_PROFILES_DIR=. /Users/diegolutckmeier/miniconda3/envs/sparkenv/bin/dbt test
```

The connection is defined in `profiles.yml`, which points dbt to `../data/finance_lakehouse.duckdb`.

