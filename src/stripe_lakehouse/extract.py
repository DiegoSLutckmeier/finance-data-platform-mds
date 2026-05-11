"""Stripe extraction orchestration."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from stripe_lakehouse.bronze_writer import build_bronze_rows, write_bronze_parquet
from stripe_lakehouse.config import Settings
from stripe_lakehouse.state import State, get_last_created, load_state, save_state, update_entity_state
from stripe_lakehouse.stripe_client import configure_stripe, iter_list_entity, retrieve_balance_snapshot


DEFAULT_ENTITIES = [
    "customers",
    "charges",
    "payment_intents",
    "payouts",
    "balance_transactions",
    "balance",
]


def extract_all(settings: Settings, entities: list[str] | None = None) -> dict[str, Path | None]:
    """Extract configured Stripe entities into Bronze Parquet files."""

    configure_stripe(settings.stripe_api_key)
    state = load_state(settings.state_path)
    load_id = str(uuid.uuid4())
    outputs: dict[str, Path | None] = {}

    for entity in entities or DEFAULT_ENTITIES:
        records = extract_entity(entity, state, settings.lookback_days)
        rows = build_bronze_rows(entity, records, load_id)
        outputs[entity] = write_bronze_parquet(settings.bronze_dir, entity, rows, load_id)

        last_created = _max_created(records) or get_last_created(state, entity)
        update_entity_state(state, entity, last_created, load_id)

    save_state(settings.state_path, state)
    return outputs


def extract_entity(entity: str, state: State, lookback_days: int) -> list[dict[str, Any]]:
    """Extract one entity, using state for CDC-style incremental list endpoints."""

    if entity == "balance":
        snapshot = retrieve_balance_snapshot()
        snapshot["id"] = f"balance_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        snapshot["created"] = int(datetime.now(timezone.utc).timestamp())
        return [snapshot]

    created_gte = _created_gte_with_lookback(get_last_created(state, entity), lookback_days)
    return list(iter_list_entity(entity, created_gte=created_gte))


def _created_gte_with_lookback(last_created: int | None, lookback_days: int) -> int | None:
    if last_created is None:
        return None

    lookback = datetime.fromtimestamp(last_created, tz=timezone.utc) - timedelta(days=lookback_days)
    return int(lookback.timestamp())


def _max_created(records: list[dict[str, Any]]) -> int | None:
    created_values = [record.get("created") for record in records if record.get("created") is not None]
    return int(max(created_values)) if created_values else None

