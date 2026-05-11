"""DuckDB helpers for local lakehouse models."""

from __future__ import annotations

from pathlib import Path

import duckdb


def connect_database(path: Path) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection and create schemas used by the lakehouse."""

    path.parent.mkdir(parents=True, exist_ok=True)
    connection = duckdb.connect(str(path))
    connection.execute("create schema if not exists bronze")
    connection.execute("create schema if not exists silver")
    connection.execute("create schema if not exists gold")
    return connection


def create_bronze_view(connection: duckdb.DuckDBPyConnection, bronze_dir: Path, entity: str) -> None:
    """Create or replace a DuckDB view over an entity's Bronze Parquet files."""

    parquet_glob = str(bronze_dir / entity / "**" / "*.parquet")
    view_name = f"bronze.stripe_{entity}"
    connection.execute(
        f"""
        create or replace view {view_name} as
        select *
        from read_parquet(?, union_by_name = true)
        """,
        [parquet_glob],
    )


def create_all_bronze_views(
    connection: duckdb.DuckDBPyConnection,
    bronze_dir: Path,
    entities: list[str],
) -> None:
    """Create Bronze views for all provided entities."""

    for entity in entities:
        create_bronze_view(connection, bronze_dir, entity)

