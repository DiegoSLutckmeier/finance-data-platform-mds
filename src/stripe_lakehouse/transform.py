"""Local transform entrypoints."""

from __future__ import annotations

from stripe_lakehouse.config import Settings
from stripe_lakehouse.duckdb_models import connect_database, create_all_bronze_views
from stripe_lakehouse.extract import DEFAULT_ENTITIES


def prepare_duckdb(settings: Settings) -> None:
    """Prepare DuckDB schemas and Bronze external views."""

    connection = connect_database(settings.duckdb_path)
    try:
        create_all_bronze_views(connection, settings.bronze_dir, DEFAULT_ENTITIES)
    finally:
        connection.close()

