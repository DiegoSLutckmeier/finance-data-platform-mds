# Airflow

Airflow is used as the orchestration layer for the local pipeline.

It does not replace Python, DuckDB, or dbt. It coordinates them.

## DAG

The DAG is:

```text
stripe_lakehouse_pipeline
```

Task order:

```text
extract_stripe_data
   |
   v
validate_bronze_files
   |
   v
create_duckdb_bronze_views
   |
   v
dbt_run
   |
   v
dbt_test
```

## Docker Services

The local Docker Compose setup uses:

- `postgres`: Airflow metadata database.
- `airflow-init`: one-time initialization container.
- `airflow-webserver`: Airflow UI.
- `airflow-scheduler`: scheduler that runs DAG tasks.

Postgres here is only for Airflow metadata. It is not the analytics database. The analytics database is DuckDB.

## Start Airflow

Build the image:

```bash
docker compose build
```

Initialize Airflow:

```bash
docker compose up airflow-init
```

Start Airflow:

```bash
docker compose up airflow-webserver airflow-scheduler
```

Open:

```text
http://localhost:8080
```

Login:

```text
username: airflow
password: airflow
```

## Maintenance

The project folder is mounted into the Airflow containers at:

```text
/opt/airflow/project
```

That means normal code and dbt changes can be made in VS Code and rerun in Airflow without rebuilding the Docker image.

Rebuild the image only when Python dependencies change.

