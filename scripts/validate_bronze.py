"""Validate Bronze Parquet outputs and extraction state."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse import config
from stripe_lakehouse.extraction.strategies import ENTITIES


REQUIRED_BRONZE_COLUMNS = {
    "entity",
    "object_id",
    "object_type",
    "raw_payload",
    "source",
    "load_id",
    "extracted_at",
    "stripe_created_at",
}


def main() -> None:
    load_dotenv()
    settings = config.load_settings()

    state_data = load_state(settings.state_path)
    failures = []

    for entity in ENTITIES:
        print(f"\nValidating {entity}")
        failures.extend(validate_entity_state(entity, state_data))
        failures.extend(validate_entity_files(entity, settings.bronze_dir))

    if failures:
        print("\nBronze validation failed")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nBronze validation passed")


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"State file does not exist: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_entity_state(entity: str, state_data: dict[str, Any]) -> list[str]:
    failures = []
    entity_state = state_data.get(entity)

    if not entity_state:
        return [f"{entity}: missing from state file"]

    if entity_state.get("status") != "success":
        failures.append(f"{entity}: last extraction status is {entity_state.get('status')}")

    if entity_state.get("last_error"):
        failures.append(f"{entity}: last_error is not empty")

    rows_loaded = entity_state.get("rows_loaded")
    if rows_loaded is None:
        failures.append(f"{entity}: rows_loaded is missing from state")

    output_path = entity_state.get("last_output_path")
    if rows_loaded == 0 and output_path is not None:
        failures.append(f"{entity}: rows_loaded is 0 but last_output_path is populated")

    if rows_loaded and not output_path:
        failures.append(f"{entity}: rows_loaded is {rows_loaded} but last_output_path is missing")

    print(f"  state status: {entity_state.get('status')}")
    print(f"  rows loaded: {rows_loaded}")

    return failures


def validate_entity_files(entity: str, bronze_dir: Path) -> list[str]:
    failures = []
    parquet_files = sorted((bronze_dir / entity).glob("**/*.parquet"))

    if not parquet_files:
        print("  parquet files: 0")
        return failures

    print(f"  parquet files: {len(parquet_files)}")

    for path in parquet_files:
        try:
            dataframe = pd.read_parquet(path)
        except Exception as exc:
            failures.append(f"{entity}: cannot read {path}: {exc}")
            continue

        missing_columns = REQUIRED_BRONZE_COLUMNS - set(dataframe.columns)
        if missing_columns:
            failures.append(f"{entity}: {path} missing columns {sorted(missing_columns)}")

        if dataframe.empty:
            failures.append(f"{entity}: {path} has zero rows")

        if "entity" in dataframe.columns:
            unexpected_entities = set(dataframe["entity"].dropna().unique()) - {entity}
            if unexpected_entities:
                failures.append(
                    f"{entity}: {path} contains unexpected entity values {sorted(unexpected_entities)}"
                )

        if "raw_payload" in dataframe.columns and dataframe["raw_payload"].isna().any():
            failures.append(f"{entity}: {path} contains null raw_payload values")

    return failures


if __name__ == "__main__":
    main()
