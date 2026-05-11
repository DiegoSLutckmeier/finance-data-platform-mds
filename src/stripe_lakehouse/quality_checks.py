"""Lightweight quality checks for local development."""

from __future__ import annotations

from pathlib import Path

import duckdb


def assert_non_empty_parquet(path: Path) -> None:
    """Fail if a Parquet file or glob has no rows."""

    with duckdb.connect() as connection:
        row_count = connection.execute(
            "select count(*) from read_parquet(?, union_by_name = true)",
            [str(path)],
        ).fetchone()[0]

    if row_count == 0:
        raise AssertionError(f"No rows found in {path}")


def assert_no_null_object_ids(database_path: Path, table_name: str) -> None:
    """Fail if a modeled table has null object IDs."""

    with duckdb.connect(str(database_path)) as connection:
        null_count = connection.execute(
            f"select count(*) from {table_name} where object_id is null"
        ).fetchone()[0]

    if null_count:
        raise AssertionError(f"{table_name} has {null_count} rows with null object_id")

