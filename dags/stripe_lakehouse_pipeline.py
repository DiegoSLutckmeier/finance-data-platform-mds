"""Airflow DAG for the local Stripe lakehouse pipeline."""

from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"
DBT_DIR = f"{PROJECT_DIR}/dbt_finance_platform"


default_args = {
    "owner": "finance-lakehouse",
    "retries": 1,
}


with DAG(
    dag_id="stripe_lakehouse_pipeline",
    description="Extract Stripe data, validate Bronze, create DuckDB views, and run dbt.",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["stripe", "lakehouse", "duckdb", "dbt"],
) as dag:
    extract_stripe = BashOperator(
        task_id="extract_stripe_data",
        bash_command=f"cd {PROJECT_DIR} && python scripts/extract_all.py",
        append_env=True,
    )

    validate_bronze = BashOperator(
        task_id="validate_bronze_files",
        bash_command=f"cd {PROJECT_DIR} && python scripts/validate_bronze.py",
        append_env=True,
    )

    create_bronze_views = BashOperator(
        task_id="create_duckdb_bronze_views",
        bash_command=f"cd {PROJECT_DIR} && python scripts/create_duckdb_bronze_views.py",
        append_env=True,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && dbt run",
        append_env=True,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_DIR} && dbt test",
        append_env=True,
    )

    extract_stripe >> validate_bronze >> create_bronze_views >> dbt_run >> dbt_test
