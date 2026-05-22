"""Load one Stripe entity into the Bronze layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from dotenv import load_dotenv

from stripe_lakehouse import bronze_writer, config, state, stripe_client
from stripe_lakehouse.extraction.strategies import describe_strategy, get_strategy


def load_entity(entity: str) -> dict[str, Any]:
    """Load one entity and return a small run summary."""

    load_dotenv()
    settings = config.load_settings()
    stripe_client.configure_stripe(settings.stripe_api_key)

    strategy = get_strategy(entity)
    state_data = state.load_state(settings.state_path)
    load_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    try:
        created_gte = calculate_created_gte(entity, strategy, state_data)
        records = extract_records(entity, strategy, created_gte)
        bronze_rows = bronze_writer.build_bronze_rows(
            entity=entity,
            records=records,
            load_id=load_id,
        )
        output_path = bronze_writer.write_bronze_parquet(
            base_dir=settings.bronze_dir,
            entity=entity,
            rows=bronze_rows,
            load_id=load_id,
        )

        newest_created = max_created(records) or state.get_last_created(state_data, entity)
        state.update_entity_state(
            state=state_data,
            entity=entity,
            last_created=newest_created,
            load_id=load_id,
        )
        state_data[entity].update(
            {
                "status": "success",
                "refresh_method": describe_strategy(strategy),
                "created_gte": created_gte,
                "started_at": started_at,
                "finished_at": datetime.now(timezone.utc).isoformat(),
                "rows_loaded": len(bronze_rows),
                "last_output_path": str(output_path) if output_path else None,
                "last_error": None,
            }
        )
        state.save_state(settings.state_path, state_data)

        return {
            "entity": entity,
            "status": "success",
            "rows_loaded": len(bronze_rows),
            "output_path": str(output_path) if output_path else None,
        }

    except Exception as exc:
        previous = state_data.get(entity, {})
        state_data[entity] = {
            **previous,
            "status": "failed",
            "refresh_method": describe_strategy(strategy),
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "last_load_id": load_id,
            "last_error": str(exc),
        }
        state.save_state(settings.state_path, state_data)
        raise


def calculate_created_gte(
    entity: str,
    strategy: dict[str, Any],
    state_data: state.State,
) -> int | None:
    if strategy["mode"] == "snapshot":
        return None

    if strategy["mode"] == "full_refresh":
        return None

    if strategy["mode"] == "lookback":
        last_created = state.get_last_created(state_data, entity)
        if last_created is None:
            return None

        lookback_start = datetime.fromtimestamp(last_created, tz=timezone.utc) - timedelta(
            days=int(strategy["days"])
        )
        return int(lookback_start.timestamp())

    raise ValueError(f"Unsupported strategy mode: {strategy['mode']}")


def extract_records(
    entity: str,
    strategy: dict[str, Any],
    created_gte: int | None,
) -> list[dict[str, Any]]:
    if strategy["mode"] == "snapshot":
        snapshot = stripe_client.retrieve_balance_snapshot()
        snapshot["id"] = f"balance_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        snapshot["created"] = int(datetime.now(timezone.utc).timestamp())
        return [snapshot]

    return list(stripe_client.iter_list_entity(entity, created_gte=created_gte))


def max_created(records: list[dict[str, Any]]) -> int | None:
    created_values = [record.get("created") for record in records if record.get("created")]
    return int(max(created_values)) if created_values else None

