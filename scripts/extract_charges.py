"""Extract Stripe charges using a 30-day lookback."""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse import bronze_writer, config, state, stripe_client


LOOKBACK_DAYS = 30


def main() -> None:
    """Run an initial full load, then 30-day lookback refreshes for charges."""

    load_dotenv()
    settings = config.load_settings()
    stripe_client.configure_stripe(settings.stripe_api_key)

    entity = "charges"
    load_id = str(uuid.uuid4())

    state_data = state.load_state(settings.state_path)
    last_created = state.get_last_created(state_data, entity)
    created_gte = calculate_created_gte(last_created)

    charges = list(stripe_client.iter_list_entity(entity, created_gte=created_gte))

    bronze_rows = bronze_writer.build_bronze_rows(
        entity=entity,
        records=charges,
        load_id=load_id,
    )
    output_path = bronze_writer.write_bronze_parquet(
        base_dir=settings.bronze_dir,
        entity=entity,
        rows=bronze_rows,
        load_id=load_id,
    )

    newest_created = max_created(charges) or last_created
    state.update_entity_state(
        state=state_data,
        entity=entity,
        last_created=newest_created,
        load_id=load_id,
    )
    state_data[entity]["refresh_method"] = f"{LOOKBACK_DAYS}_day_lookback"
    state_data[entity]["created_gte"] = created_gte
    state_data[entity]["rows_loaded"] = len(bronze_rows)
    state_data[entity]["last_output_path"] = str(output_path) if output_path else None
    state.save_state(settings.state_path, state_data)

    print(f"Loaded {len(bronze_rows)} charges")
    print(f"Created filter: {created_gte}")
    print(f"Bronze file: {output_path}")
    print(f"State file: {settings.state_path}")


def calculate_created_gte(last_created: int | None) -> int | None:
    """Return None for first load, otherwise last_created minus the lookback window."""

    if last_created is None:
        return None

    lookback_start = datetime.fromtimestamp(last_created, tz=timezone.utc) - timedelta(
        days=LOOKBACK_DAYS
    )
    return int(lookback_start.timestamp())


def max_created(records: list[dict]) -> int | None:
    """Return the newest Stripe created timestamp from extracted records."""

    created_values = [record.get("created") for record in records if record.get("created")]
    return int(max(created_values)) if created_values else None


if __name__ == "__main__":
    main()
