"""JSON state management for incremental Stripe extraction."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


State = dict[str, dict[str, Any]]


def load_state(path: Path) -> State:
    """Load extraction state from disk, returning an empty state if it does not exist."""

    if not path.exists():
        return {}

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(path: Path, state: State) -> None:
    """Persist extraction state as readable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, sort_keys=True)
        file.write("\n")


def get_last_created(state: State, entity: str) -> int | None:
    """Return the last Stripe created timestamp for an entity."""

    value = state.get(entity, {}).get("last_created")
    return int(value) if value is not None else None


def update_entity_state(state: State, entity: str, last_created: int | None, load_id: str) -> State:
    """Update state after a successful entity extraction."""

    state[entity] = {
        "last_created": last_created,
        "last_successful_sync": datetime.now(timezone.utc).isoformat(),
        "last_load_id": load_id,
    }
    return state

