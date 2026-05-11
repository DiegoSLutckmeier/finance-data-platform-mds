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


ENTITY_REFRESH_STRATEGIES = {
    "customers": {"mode": "full_refresh"},
    "charges": {"mode": "lookback", "days": 30},
    "payment_intents": {"mode": "lookback", "days": 30},
    "payouts": {"mode": "lookback", "days": 30},
    "balance_transactions": {"mode": "lookback", "days": 7},
    "balance": {"mode": "snapshot"},
}


def extract_all(settings: Settings, entities: list[str] | None = None) -> dict[str, Path | None]:
    """Extract configured Stripe entities into Bronze Parquet files."""

    configure_stripe(settings.stripe_api_key)
    state = load_state(settings.state_path)
    outputs: dict[str, Path | None] = {}

    for entity in entities or DEFAULT_ENTITIES:
        load_id = str(uuid.uuid4())
        records = extract_entity(entity, state)
        rows = build_bronze_rows(entity, records, load_id)
        outputs[entity] = write_bronze_parquet(settings.bronze_dir, entity, rows, load_id)

        last_created = _max_created(records) or get_last_created(state, entity)
        update_entity_state(state, entity, last_created, load_id)
        save_state(settings.state_path, state)

    return outputs


def extract_one(settings: Settings, entity: str) -> Path | None:
    """Extract one Stripe entity into its own Bronze Parquet load."""

    configure_stripe(settings.stripe_api_key)
    state = load_state(settings.state_path)
    load_id = str(uuid.uuid4())

    records = extract_entity(entity, state)
    rows = build_bronze_rows(entity, records, load_id)
    output = write_bronze_parquet(settings.bronze_dir, entity, rows, load_id)

    last_created = _max_created(records) or get_last_created(state, entity)
    update_entity_state(state, entity, last_created, load_id)
    save_state(settings.state_path, state)

    return output


def extract_entity(entity: str, state: State) -> list[dict[str, Any]]:
    """Extract one entity using its configured refresh strategy."""

    strategy = ENTITY_REFRESH_STRATEGIES.get(entity)
    if strategy is None:
        raise ValueError(f"Unsupported Stripe entity: {entity}")

    if strategy["mode"] == "snapshot":
        snapshot = retrieve_balance_snapshot()
        snapshot["id"] = f"balance_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        snapshot["created"] = int(datetime.now(timezone.utc).timestamp())
        return [snapshot]

    if strategy["mode"] == "full_refresh":
        return list(iter_list_entity(entity, created_gte=None))

    created_gte = _created_gte_with_lookback(
        get_last_created(state, entity),
        int(strategy["days"]),
    )
    return list(iter_list_entity(entity, created_gte=created_gte))


def _created_gte_with_lookback(last_created: int | None, lookback_days: int) -> int | None:
    if last_created is None:
        return None

    lookback = datetime.fromtimestamp(last_created, tz=timezone.utc) - timedelta(days=lookback_days)
    return int(lookback.timestamp())


def _max_created(records: list[dict[str, Any]]) -> int | None:
    created_values = [record.get("created") for record in records if record.get("created") is not None]
    return int(max(created_values)) if created_values else None
