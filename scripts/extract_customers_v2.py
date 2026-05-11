"""V2 learning script: extract Stripe customers using small helper modules."""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT / "src"))

from stripe_lakehouse.bronze_writer import build_bronze_rows, write_bronze_parquet
from stripe_lakehouse.config import load_settings
from stripe_lakehouse.state import load_state, save_state, update_entity_state
from stripe_lakehouse.stripe_client import configure_stripe, iter_list_entity


def main() -> None:
    """Run a full refresh of Stripe customers into Bronze."""

    load_dotenv()
    settings = load_settings()
    configure_stripe(settings.stripe_api_key)

    entity = "customers"
    load_id = str(uuid.uuid4())

    customers = list(iter_list_entity(entity, created_gte=None))

    bronze_rows = build_bronze_rows(
        entity=entity,
        records=customers,
        load_id=load_id,
    )
    output_path = write_bronze_parquet(
        base_dir=settings.bronze_dir,
        entity=entity,
        rows=bronze_rows,
        load_id=load_id,
    )

    state = load_state(settings.state_path)
    update_entity_state(
        state=state,
        entity=entity,
        last_created=None,
        load_id=load_id,
    )
    state[entity]["refresh_method"] = "full_refresh"
    state[entity]["rows_loaded"] = len(bronze_rows)
    state[entity]["last_output_path"] = str(output_path) if output_path else None
    save_state(settings.state_path, state)

    print(f"Loaded {len(bronze_rows)} customers")
    print(f"Bronze file: {output_path}")
    print(f"State file: {settings.state_path}")


if __name__ == "__main__":
    main()
