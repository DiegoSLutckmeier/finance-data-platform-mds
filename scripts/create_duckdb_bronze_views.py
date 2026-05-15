"""Create DuckDB Bronze views over local Stripe Parquet files."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse import config
from stripe_lakehouse.extraction.strategies import ENTITIES


def main() -> None:
    load_dotenv()
    settings = config.load_settings()

    connection = duckdb.connect(str(settings.duckdb_path))
    try:
        connection.execute("create schema if not exists bronze")

        for entity in ENTITIES:
            create_bronze_view(
                connection=connection,
                bronze_dir=settings.bronze_dir,
                entity=entity,
            )

        print(f"DuckDB database: {settings.duckdb_path}")
        print("Created Bronze views:")
        for entity in ENTITIES:
            view_name = f"bronze.stripe_{entity}"
            row_count = connection.execute(f"select count(*) from {view_name}").fetchone()[0]
            print(f"- {view_name}: {row_count} rows")
    finally:
        connection.close()


def create_bronze_view(
    connection: duckdb.DuckDBPyConnection,
    bronze_dir: Path,
    entity: str,
) -> None:
    parquet_glob = str(bronze_dir / entity / "**" / "*.parquet")
    view_name = f"bronze.stripe_{entity}"

    if not list((bronze_dir / entity).glob("**/*.parquet")):
        connection.execute(
            f"""
            create or replace view {view_name} as
            select
                cast(null as varchar) as entity,
                cast(null as varchar) as object_id,
                cast(null as varchar) as object_type,
                cast(null as varchar) as raw_payload,
                cast(null as varchar) as source,
                cast(null as varchar) as load_id,
                cast(null as varchar) as extracted_at,
                cast(null as bigint) as stripe_created_at
            where false
            """
        )
        return

    escaped_parquet_glob = parquet_glob.replace("'", "''")
    connection.execute(
        f"""
        create or replace view {view_name} as
        select *
        from read_parquet('{escaped_parquet_glob}', union_by_name = true)
        """
    )


if __name__ == "__main__":
    main()
