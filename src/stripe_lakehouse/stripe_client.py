"""Stripe API client helpers."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import stripe


LIST_ENDPOINTS = {
    "customers": stripe.Customer,
    "charges": stripe.Charge,
    "payment_intents": stripe.PaymentIntent,
    "payouts": stripe.Payout,
    "balance_transactions": stripe.BalanceTransaction,
}


def configure_stripe(api_key: str) -> None:
    """Configure the global Stripe client."""

    stripe.api_key = api_key


def iter_list_entity(entity: str, created_gte: int | None = None) -> Iterator[dict[str, Any]]:
    """Yield every object for a paginated Stripe list endpoint."""

    resource = LIST_ENDPOINTS[entity]
    params: dict[str, Any] = {"limit": 100}
    if created_gte is not None:
        params["created"] = {"gte": created_gte}

    for item in resource.list(**params).auto_paging_iter():
        yield stripe_object_to_dict(item)


def retrieve_balance_snapshot() -> dict[str, Any]:
    """Retrieve Stripe's current balance snapshot."""

    return stripe_object_to_dict(stripe.Balance.retrieve())


def stripe_object_to_dict(item: Any) -> dict[str, Any]:
    """Convert Stripe SDK objects into plain Python dictionaries."""

    if hasattr(item, "to_dict_recursive"):
        return item.to_dict_recursive()

    if hasattr(item, "to_dict"):
        return item.to_dict()

    if hasattr(item, "_to_dict_recursive"):
        return item._to_dict_recursive()

    return dict(item)
