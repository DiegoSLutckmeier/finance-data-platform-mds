"""Refresh strategies for each Stripe entity."""

from __future__ import annotations

from typing import Any


ENTITY_STRATEGIES: dict[str, dict[str, Any]] = {
    "customers": {"mode": "full_refresh"},
    "charges": {"mode": "lookback", "days": 30},
    "payment_intents": {"mode": "lookback", "days": 30},
    "payouts": {"mode": "lookback", "days": 30},
    "balance_transactions": {"mode": "lookback", "days": 7},
    "balance": {"mode": "snapshot"},
}


ENTITIES = list(ENTITY_STRATEGIES)


def get_strategy(entity: str) -> dict[str, Any]:
    strategy = ENTITY_STRATEGIES.get(entity)
    if strategy is None:
        raise ValueError(f"Unsupported entity: {entity}")
    return strategy


def describe_strategy(strategy: dict[str, Any]) -> str:
    if strategy["mode"] == "lookback":
        return f"{strategy['days']}_day_lookback"
    return str(strategy["mode"])

